from pydantic import BaseModel
import importlib

from models import *
from grs import *
from rs import *
from sim import simulate

class DataBase(BaseModel):
    items: dict[str, list[Item]] = {}
    users: dict[str, list[User]] = {}
    consumptions: dict[tuple[str, str], list[Consumption]] = {}
    productions: dict[tuple[str, str], list[Production]] = {}
    item_inter: dict[str, list[Item_Inter]] = {}
    user_inter: dict[str, list[User_Inter]] = {}

    ids: list[str] = []
    atribs: dict[str, list[str]] = {}
    users_sign: list[str] = []
    inter: dict[str, dict[tuple[str, str, str], list[str]]] = {}
    thread_collab: dict = {}
    thread_content: dict = {}
    similar_collab: dict = {}
    similar_content: dict = {}
    simulators: dict = {'llm': simulate}

    def __init__(self, url: str, detect_atrib: bool = True, atribs: dict[str, dict[str, list[str]]] = {},
                    users_sign: list[str] = [], detect_inter: bool = True,
                    inter: dict[str, dict[tuple[str, str, str], list[str]]] = {}, sim_content: dict[str, FunctionType] = {}):
        super().__init__()
        charge_database(self, url, detect_atrib, atribs, users_sign, detect_inter, inter, sim_content)
        
        for id in self.thread_content:
            Thread(target=self.thread_content_func, args=(id, )).start()

    def __repr__(self):
       return f"DataBase(users_count={len(self.users)}, items_count={len(self.items)})"

    def set_merx(self, ids, atribs, users_sign, inter):
        self.ids = ids
        self.atribs = atribs.copy()
        self.users_sign = users_sign.copy()
        self.inter = inter.copy()

    def set_sim_content(self, sim_content, url):
        for k, v in sim_content.items():
            self.thread_content[k] = v

        tmp = {}
        for f in self.atribs:
            for k in self.atribs[f]:
                if not k in self.thread_content: 
                    if not k in tmp: tmp[k] = set([])
                    tmp[k].update(self.atribs[f][k])

        for k in tmp:
            if len(tmp[k]) > 0:
                types = detect_type(k, tmp[k], self.atribs, url)
                response, code = get_sim(url, tmp[k], types)

                try:
                    with open(f'{k}.py', 'w', encoding='utf-8') as f:
                        f.write(code)
                    module = importlib.import_module(f'{k}')
                    self.thread_content[k] = getattr(module, response)
                except Exception as e:
                    print(e)

    def thread_content_func(self, id):
        while True:
            print(f'filter content in {id} started')
            
            if id in self.items:
                self.similar_content[id] = {}
                for i in range(len(self.items[id])):
                    for j in range(i+1, len(self.items[id])):
                        try:
                            val = self.thread_content[id](self.items[id][i], self.items[id][j])
                        except:
                            val = 0
                        if isnan(val) or val is None: val = 0
                        self.similar_content[id][(self.items[id][i].id, self.items[id][j].id)] = val

            elif id in self.users:
                self.similar_content[id] = {}
                for i in range(len(self.users[id])):
                    for j in range(i+1, len(self.users[id])):
                        try:
                            val = self.thread_content[id](self.users[id][i], self.users[id][j])
                        except:
                            val = 0
                        if isnan(val) or val is None: val = 0
                        self.similar_content[id][(self.users[id][i].id, self.users[id][j].id)] = val

            print(f'filter content in {id} finished')
            time.sleep(300)

    def create_user(self, key, data):
        created = False
        
        if key in self.users:
            pos = binary_search_lte(self.users[key], data[key])
            if self.users[key][pos].id == data[key]:
                created = True
                self.users[key][pos].set_args(dup(data, key))
        else:
            pos = -1
            self.users[key] = []

        if not created:
            pos += 1
            self.users[key].insert(pos, User(id=str(data[key]), args=dup(data, key)))

        return pos, created
    
    def create_item(self, key, data):
        created = False
        
        if key in self.items:
            pos = binary_search_lte(self.items[key], data[key])
            if self.items[key][pos].id == data[key]:
                created = True
                self.items[key][pos].set_args(dup(data, key))
        else:
            pos = -1
            self.items[key] = []

        if not created:
            pos += 1
            self.items[key].insert(pos, Item(id=str(data[key]), args=dup(data, key)))

        return pos, created
    
    def create_interaction(self, data, type, add_list, rel, keys, *ids):
        created = False
        if keys in add_list:
           
            if type == Consumption or type == Production:
                for par in add_list[keys]:
                    if par.user.id == ids[0].id and par.item.id == ids[1].id:
                        created = True
                        par.set_args(data)
                        break

            else:
                for par in add_list[keys]:
                    if par.info == rel:
                        created = True
                        par.add_inter(data, *ids)
                        break

        else:
            add_list[keys] = []

        if not created:
            if type == Consumption or type == Production:
                add_list[keys].append(type(user=ids[0], item=ids[1], args=data))
            else:
                add_list[keys].append(type(rel, data, *ids))

    def take(self, obj, list, id_group = None):
        if id_group is None:
            for id_group in list:
                pos = binary_search_lte(list[id_group], obj)
                if list[id_group][pos].id == obj:
                    return list[id_group][pos], id_group
        pos = binary_search_lte(list[id_group], obj)
        if list[id_group][pos].id == obj:
            return list[id_group][pos]
        raise Exception(f'{obj} not found in list with id {id_group}')
    
    def inst_action(self, user, action):
        if type(user) == User:
            user.inst_actions(action)

        else:
            try:
                user, _ = self.take(user, self.users)
                # match with predefined actions
                user.inst_actions(action)
            except:
                print(f'User {user} Not Found')

    def make_interaction(self, user, act, id, elements: dict, type):
        try:
            user, id_group = self.take(user, self.users)

            ids = list(elements.keys())
            ids.remove(id)
            for a in range(len(ids)-1, -1, -1):
                if not ids[a] in self.ids: ids.pop(a)

            if id in self.users_sign:
                pos, created = self.create_user(id, elements)
                obj = 'user'
                obj_tmp = self.users[id][pos]
            else:
                pos, created = self.create_item(id, elements)
                obj = 'item'
                obj_tmp = self.items[id][pos]
        
            inters = {}
            for file in self.inter:
                for inter in self.inter[file]:
                    if obj == 'item':
                        if inter == (id_group, id, type) or inter == (id, id_group, type):
                            inters[inter] = self.inter[file][inter]
                    else:
                        if (inter[0] == id_group and inter[1] == id) or (inter[0] == id and inter[1] == id_group):
                            inters[inter] = self.inter[file][inter]

                    for i in ids:
                        if (inter[0] == i and inter[1] == id) or (inter[0] == id and inter[1] == i):
                            inters[inter] = self.inter[file][inter]

            for i in inters:
                if id_group == i[0]:
                    obj1, obj2 = user, obj_tmp
                elif id_group == i[1]:
                    obj1, obj2 = obj_tmp, user
                else:
                    try:
                        if id == i[0]:
                            obj1 = obj_tmp
                            if obj == 'item':
                                obj2, _ = self.take(elements[i[1]], self.items)
                            else:
                                obj2, _ = self.take(elements[i[1]], self.users)
                        else:
                            obj2 = obj_tmp
                            if obj == 'item':
                                obj1, _ = self.take(elements[i[0]], self.items)
                            else:
                                obj1, _ = self.take(elements[i[0]], self.users)
                    except:
                        print(f'Object Not Found')

                if i[2] == 'production':
                    obj1.produce(id, obj2)
                    obj2.set_producer(id_group, obj1)
                    self.create_interaction(clean(elements, inters[i]), Production, self.productions, None, (i[0], i[1]), obj1, obj2)
                elif i[2] == 'consumption':
                    obj1.consume(id, obj2)
                    obj2.set_consumer(id_group, obj1)
                    self.create_interaction(clean(elements, inters[i]), Consumption, self.consumptions, None, (i[0], i[1]), obj1, obj2)
                elif obj == 'item':
                    self.create_interaction(clean(elements, inters[i]), Item_Inter, self.item_inter, i[2], (i[0], i[1]), obj1, obj2)
                else:
                    self.create_interaction(clean(elements, inters[i]), User_Inter, self.user_inter, i[2], (i[0], i[1]), obj1, obj2)

            self.inst_action(user, act)


        except Exception as e:
            print(e)

    def db_recommend(self, user: str, id: str, motive: str, count: int, groups: int = 1, proportion: tuple = (0.5, 0.5),
              retrievals: list = [retrieval_exist], scores: list = [score_triangle, score_produce, score_co_consumer, score_consume]):
        return recommend(self, user, id, motive, count, groups, retrievals, scores, proportion)
    
    def add_simulator(self, key, func):
        self.simulators[key] = func

    def simulation(self, user, recommends, key, objetive, type: str = 'llm'):
        for k in self.simulators:
            if type == k:
                return self.simulators[k](self, user, recommends, key, objetive)
        else:
            raise Exception('The simulation type does\'n exist')

