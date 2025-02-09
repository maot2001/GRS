from database import *

class Seen(BaseModel):
    user: User
    element: Item | User
    args: dict

    def set_args(self, args: dict):
        self.args.update(args)

def get_inherited_atribs(url: str, atribs: dict = {}, count = 1):
    """
    It is responsible for determining which attributes correspond to each id that belongs to a inherited key.

    Args:
        url: root address of the database.
        atribs: dictionary that can contain the distribution of attributes for specific files, which will not be reviewed in the
                analysis.
        count: number of times the query is to be performed, which allows the LLM's capacity to be tested.

    Returns:
        list: if count is 1, only the response dict is returned in type dict;
              if it is greater than 1, the list containing the response dicts is returned.
    """
    txt_atribs = {}
    responses = []

    with open(os.path.join(url, 'atrib.txt'), 'r', encoding='utf-8') as f:
        atrib = f.read().split('\n')
        for text in atrib:
            ind = text.index(' ')
            txt_atribs[text[:ind]] = text[ind:]

    inherited = set([])
    for _ in range(count):
        this_atribs = atribs.copy()
        
        for name_data in os.listdir(url):
            if not name_data.endswith('.csv'): continue
            if name_data[:-4] in this_atribs: continue

            data = pd.read_csv(os.path.join(url, name_data))
            
            elements = []
            for col in data.head():
                elements.append(col)

            msg = f'In a file named "{name_data[:-4]}" there are these elements with their descriptions:\n'
                
            for atrib in txt_atribs:
                if atrib in elements:
                    msg += f'{atrib}{txt_atribs[atrib]}\n'

            tmp = f', inherited objects that already exist are {', '.join(list(inherited))}' if len(inherited) > 0 else ''
            msg += f'Please tell me what id the attributes without id belong to, I only want the ids that represent an inherited key, also note that I only want attributes that relate to a single id. I want you to join the parent id "a-id" with the child id "b-id" like this "a-id_b-id". An object can only have one parent, which means "a-id_b-id" and "c-id_b-id" cannot exist at the same time. They also cannot form a cycle like "a-id_b-id" and "b-id_a-id"{tmp}.'
            msg += ', return them in the following format \n{"a-id_b-id": ["a_val", "name"],\n"a-id_d-id": ["url"]}\nIf you don\'t find any object with an inherited key then return {}\nIt is very important that you put the curly braces when answering {}'

            response = None
            while response is None:
                response = llama_acces(msg)
                if response is None: continue

                sons = []
                for k in reversed(list(response.keys())):
                    if not '_' in k:
                        response.pop(k)
                        continue
                    
                    son = k.split('_')[-1]
                    if not '-id' in son or son == 'time-id':
                        response.pop(k)
                        continue

                    if not son in sons: sons.append(son)
                    else:
                        response = None
                        break

                if not response is None: inherited.update(list(response.keys()))

            this_atribs[name_data[:-4]] = response.copy()

        responses.append(this_atribs)

    if count == 1:
        responses = responses[0]
    return responses

def get_inherited_inter(url: str, users_sign: list = [], inherited: list = [], inter: dict = {}, count = 1):
    """
    It is responsible for determining which attributes correspond to each interrelation between objects that belong to
    inherited keys.

    Args:
        url: root address of the database.
        users_sign: list of ids that correspond to users.
        inherited: list of ids that correspond to inherited keys.
        inter: dictionary that can contain the distribution of attributes for the interrelationships of specific files, which
               will not be reviewed in the analysis.
        count: number of times the query is to be performed, which allows the LLM's capacity to be tested.

    Returns:
        list: if count is 1, only the response dict is returned in type dict;
              if it is greater than 1, the list containing the response dicts is returned.
    """
    txt_atribs = {}
    responses = []

    with open(os.path.join(url, 'atrib.txt'), 'r', encoding='utf-8') as f:
        atrib = f.read().split('\n')
        for text in atrib:
            ind = text.index(' ')
            txt_atribs[text[:ind]] = text[ind:]

    rel = {}
    for id in inherited:
        son = id.split('_')[-1]
        rel[son] = id

    for _ in range(count):
        this_inter = inter.copy()
        
        for name_data in os.listdir(url):
            if not name_data.endswith('.csv'): continue
            if name_data[:-4] in this_inter: continue
            
            data = pd.read_csv(os.path.join(url, name_data))
            
            elements = []
            for col in data.head():
                elements.append(col)

            tmp = []
            for son in rel:
                if son in elements: tmp.append(son)

            if len(tmp) == 0: continue

            msg = f'In a file named "{name_data[:-4]}" there are these elements with their descriptions:\n'
                
            for atrib in txt_atribs:
                if atrib in elements:
                    msg += f'{atrib}{txt_atribs[atrib]}\n'

            msg += 'The inherited objects are: '
            msg += ', '.join(tmp)
            msg += '\nWhat are the interrelations that exist between the ids that represent inherited objects? Associate the attributes that you consider relevant to each interrelation, whether they are id or not.\nThe user ids are the following: '
            msg += ', '.join(users_sign)
            msg += '\nFor relationships between users and objects, define whether the user produces the object or consumes it with the keywords "production" and "consumption". In the case of a relationship between users or a relationship between objects, define it with a name that begins with a capital letter.\nReturn them in the following format:\n{"(p-id, a-id_b-id, consumption)": ["c-id", "name"]\n"(a-id, c-id_d-id, production)": []\n"(a-id_b-id, c-id_d-id, Belong)": ["timeStamp"]}\nIt is very important that you put the braces when answering {}'

            response = None
            while response is None:
                response = llama_acces(msg)
                if response is None: continue

                for k in reversed(list(response.keys())):
                    k2 = k
                    if isinstance(k, str):
                        k2 = k[1:-1].split(', ')

                    pos1 = True if k2[0] in tmp else False
                    pos2 = True if k2[1] in tmp else False

                    if pos1 or pos2:
                        obj1 = rel[k2[0]] if pos1 else k2[0]
                        obj2 = rel[k2[1]] if pos2 else k2[1]
                        response[(obj1, obj2, k2[2])] = response[k]

                    response.pop(k)

            this_inter[name_data[:-4]] = response.copy()

        responses.append(this_inter)
                    

    if count == 1:
        responses = responses[0]

    return responses

class DataBase2(DataBase):
    seen: dict[tuple[str, str], list[Seen]] = {}

    def __init__(self, url: str, detect_atrib: bool = True, atribs: dict[str, dict[str, list[str]]] = {},
                    users_sign: list[str] = [], detect_inter: bool = True,
                    inter: dict[str, dict[tuple[str, str, str], list[str]]] = {}, sim_content: dict[str, FunctionType] = {},
                    detect_inherited_atrib: bool = True, inherited_atribs: dict[str, dict[str, list[str]]] = {},
                    detect_inherited_inter: bool = True, inherited_inter: dict[str, dict[tuple[str, str, str], list[str]]] = {},
                    inherited_sim_content: dict[str, FunctionType] = {}):
        
        super().__init__(url, detect_atrib, atribs, users_sign, detect_inter, inter, sim_content)

        inherited = inherited_atribs.copy()
        if detect_inherited_atrib:
            inherited = get_inherited_atribs(url, inherited_atribs)

        tmp, sons = [], []
        for key in inherited:
            for id in inherited[key]:
                if not id in tmp:
                    tmp.append(id)
                    
                son = id.split('_')[-1]
                if not son in sons:
                    sons.append(son)

                obj = 'item'
                
                if son in self.users_sign:
                    self.users_sign.remove(son)
                    self.users_sign.append(id)
                    self.users[id] = self.users[son]
                    self.users.pop(son)
                    obj = 'user'

                    for i_g in self.items:
                        for i in self.items[i_g]:
                            if son in i.consumers:
                                i.consumers[id] = i.consumers[son]
                                i.consumers.pop(son)
                            if son in i.producers:
                                i.producers[id] = i.producers[son]
                                i.producers.pop(son)

                if son in self.ids:
                    self.ids.remove(son)
                    self.ids.append(id)

                    if son in self.thread_content:
                        self.thread_content[id] = self.thread_content[son]
                        self.thread_content.pop(son)

                    if son in self.items:
                        self.items[id] = self.items[son]
                        self.items.pop(son)

                        for u_g in self.users:
                            for u in self.users[u_g]:
                                if son in u.consumptions:
                                    u.consumptions[id] = u.consumptions[son]
                                    u.consumptions.pop(son)
                                if son in u.productions:
                                    u.productions[id] = u.productions[son]
                                    u.productions.pop(son)

                    for f in self.inter:
                        for i in reversed(list(self.inter[f].keys())):

                            pos1 = (i[0] == son)
                            pos2 = (i[1] == son)

                            if pos1 or pos2:
                                obj1 = id if pos1 else i[0]
                                obj2 = id if pos2 else i[1]
                                self.inter[f][(obj1, obj2, i[2])] = self.inter[f][i]

                                if i[2] == 'consumption': self.__rename__(id, self.consumptions, pos1, pos2, (i[0], i[1]))
                                elif i[2] == 'production': self.__rename__(id, self.productions, pos1, pos2, (i[0], i[1]))
                                elif obj == 'user': self.__rename__(id, self.user_inter, pos1, pos2, (i[0], i[1]))
                                elif obj == 'item': self.__rename__(id, self.item_inter, pos1, pos2, (i[0], i[1]))
                                
                                self.inter[f].pop(i)

                    for f in self.atribs:
                        for i in reversed(list(self.atribs[f].keys())):
                            if i == son:
                                self.atribs[f][id] = self.atribs[f][i]
                                self.atribs[f].pop(i)

        inter = inherited_inter.copy()
        if detect_inherited_inter:
            inter = get_inherited_inter(url, self.users_sign, tmp, inter)

        for key in self.inter:
            if key in inter:
                self.inter[key].update(inter[key])

        for key in self.atribs:
            if key in inherited:
                self.atribs[key].update(inherited[key])

        for name_data in os.listdir(url):
            if not name_data.endswith('.csv'): continue
            this_inter = inter.get(name_data[:-4], {})
            this_atribs = inherited.get(name_data[:-4], {})

            data = pd.read_csv(os.path.join(url, name_data))

            ids = {}
            for col in data.head():
                if col.endswith('-id') and col != 'time-id' and col in sons:
                    ind = sons.index(col)
                    ids[tmp[ind]] = col

            
            for i, row in data.iterrows():
                pos_user, pos_item = {}, {}
            
                for id in self.ids:
                    old_id = ids.get(id, id)
                    atr = this_atribs.get(id, [])
                    try:
                        if id in self.users_sign:
                            pos_user[id], _ = self.create_user(id, clean(row, atr, old_id, id))

                        else:
                            pos_item[id], _ = self.create_item(id, clean(row, atr, old_id, id))
                    except:
                        pass

                for var in this_inter:
                    obj1, obj2 = None, None

                    if var[0] == var[1]:
                        tmp1 = var[0]
                        tmp2 = var[1][:-4] + '2' + var[1][-3:]
                    else:
                        tmp1 = var[0]
                        tmp2 = var[1]

                    try:
                    
                        if var[2] == 'consumption' or var[2] == 'production':
                            if var[0] in pos_user and var[1] in pos_item:
                                obj1 = self.users[var[0]][pos_user[tmp1]]
                                obj2 = self.items[var[1]][pos_item[tmp2]]

                            elif var[0] in pos_item and var[1] in pos_user:
                                obj1 = self.users[var[1]][pos_user[tmp2]]
                                obj2 = self.items[var[0]][pos_item[tmp1]]

                            if not obj1 is None and not obj2 is None:
                                try:
                                    if var[2] == 'consumption':
                                        obj1.consume(var[1], obj2)
                                        obj2.set_consumer(var[0], obj1)
                                        self.create_interaction(clean(row, this_inter[var]), Consumption, self.consumptions, None, (var[0], var[1]), obj1, obj2)
                                    else:
                                        obj1.produce(var[1], obj2)
                                        obj2.set_producer(var[0], obj1)
                                        self.create_interaction(clean(row, this_inter[var]), Production, self.productions, None, (var[0], var[1]), obj1, obj2)
                                except Exception as e:
                                    print(e)

                        else:
                            user = True
                            if var[0] in pos_user and var[1] in pos_user:
                                obj1 = self.users[var[0]][pos_user[tmp1]]
                                obj2 = self.users[var[1]][pos_user[tmp2]]

                            elif var[0] in pos_item and var[1] in pos_item:
                                user = False
                                obj1 = self.items[var[0]][pos_item[tmp1]]
                                obj2 = self.items[var[1]][pos_item[tmp2]]

                            if not obj1 is None and not obj2 is None:
                                try:
                                    pass
                                    if user and obj1 != obj2:
                                        self.create_interaction(clean(row, this_inter[var]), User_Inter, self.user_inter, var[2], (var[0], var[1]), obj1, obj2)
                                    else:
                                        self.create_interaction(clean(row, this_inter[var]), Item_Inter, self.item_inter, var[2], (var[0], var[1]), obj1, obj2)
                                except Exception as e:
                                    print(e)
                    
                    except Exception as e:
                        print(e)
                    
                    pass

                if i > 1000: break
            print(name_data)

        self.set_sim_content(inherited_sim_content, url)

    def __rename__(self, id, rename_list, pos1, pos2, inter):
        if inter in rename_list:
            if pos1 and pos2:
                rename_list[(id, id)] = rename_list[inter]
            elif pos1:
                rename_list[(id, inter[1])] = rename_list[inter]
            else:
                rename_list[(inter[0], id)] = rename_list[inter]
            rename_list.pop(inter)

    def set_merx2(self, atribs, inter):
        for key in self.atribs:
            if key in atribs:
                self.atribs[key].update(atribs[key])

        for key in self.inter:
            if key in inter:
                self.inter[key].update(inter[key])

    def create_interaction(self, data, type, add_list, rel, keys, *ids):
        if type == Seen:
            created = False
            if keys in add_list:
            
                    for par in add_list[keys]:
                        if par.user.id == ids[0].id and par.element.id == ids[1].id:
                            created = True
                            par.set_args(data)
                            break

            else:
                add_list[keys] = []

            if not created:
                add_list[keys].append(type(user=ids[0], element=ids[1], args=data))

        else:
            super().create_interaction(data, type, add_list, rel, keys, *ids)
        
    def make_interaction(self, user, act, id, elements, type):
        if type == 'seen':
            try:
                user, id_group = self.take(user, self.users)
                if id in self.users_sign:
                    element, _ = self.take(elements[id], self.users)
                else:
                    element, _ = self.take(elements[id], self.items)

                
                self.create_interaction(dup(elements, id), Seen, self.seen, None, (id_group, id), user, element)
                self.inst_action(user, act)

            except Exception as e:
                print(e)

        else:
            super().make_interaction(user, act, id, elements, type)

