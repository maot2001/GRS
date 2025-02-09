from random import choice, randint
from datetime import datetime
import time
from random_words import RandomWords

from database import DataBase, one_item, item_related
from database2 import DataBase2
from player import Player, Bayesian_Network

rw = RandomWords()

class Client():
    def __init__(self, id, args):
        self.id = id
        self.args = args
        self.player = Player()
        self.models = [Bayesian_Network(1, None, None)]
        self.llm_next = []
        self.counts = [[[0, 0, 0]], [[0, 0, 0]]]
        self.predicts = []

    def set_actions(self):
        self.using = False
        self.actions = []
        self.view = 'init'
        self.this_pub = 0
        self.values_pub = None
        self.components = {}
        self.cant_recs = 0

    def do_something(self):
        action = self.player.do_act(self.values_pub[0], self.values_pub[1])

        for i in range(len(self.predicts)):
            if action == self.predicts[i]:
                self.counts[i][-1] += 1

        self.models[0].insert((action, self.values_pub[0]>.5, self.values_pub[1]>.5))

        self.actions.append(action)
        self.predicts.clear()

        return action
    
    def predict(self, recommends):
        contents, collabs = {}, {}
        user, _ = db.take(c.id, db.users)
        counts = 0
        best = None

        for l in range(len(recommends)):
            for r in recommends[l]:
                if not r in contents:
                    contents[r] = one_item(db, 'p-id', r, item_related(user, 'p-id'))
                    collabs[r] = db.similar_collab[('u-id', 'p-id')][user.id][r]

            another_bay = self.models[0].copy()
            this_c = 0
            this_a = 0

            for r in recommends[l]:
                act = ''
                while act != 'scroll' and this_a < 50:
                    act = another_bay.predict((contents[r]>.5, collabs[r]>.5))
                        
                    if act == 'like' or act == 'unlike':
                        this_c += 1
                    elif act == 'init' or act == 'publish' or act == 'create_group' or act == 'follow' or act == 'include_group':
                        break
                        
                    another_bay.insert((act, contents[r]>.5, collabs[r]>.5))

                    this_a += 1
                    
                if this_a >= 50: break
                if act == 'init' or act == 'publish' or act == 'create_group' or act == 'follow' or act == 'include_group':
                    break

            if this_c > counts:
                counts = this_c
                best = l

        return best

    def rec_view(self):
        if self.view == 'init':
            self.this_pub = 0
            self.values_pub = None
            self.components = {}
            return {
                'u-id' : 5,
                'g-id_p-id' : 10,
                'g-id' : 3,
            }
        elif self.view == 'scroll':
            self.this_pub += 1
            self.values_pub = None
            if self.this_pub % 10 == 0:
                return {
                    'g-id_p-id' : 10
                }
        else:
            return {}

    def change_view(self, act):
        if act == 'init' or act == 'publish' or act == 'create_group' or act == 'follow' or act == 'include_group':
            self.view = 'init'
        elif act == 'scroll':
            self.view = 'scroll'
        else:
            self.view = 'static'

    def show(self, recommends):
        if len(self.components) == 0:
            self.components.update(recommends)
        else:
            for key in recommends:
                self.components[key].extend(recommends[key])


def client_actions(client: Client, db: DataBase, act: str):
    if act == 'include_group':
        group_ids = client.components['g-id']
        if len(group_ids) > 0:
            group = choice(group_ids)
            db.make_interaction(client.id, act, 'g-id', {'g-id': group}, 'consumption')

    elif act == 'publish':
        text = ' '.join(rw.random_words(count=randint(5, 100)))
        db.make_interaction(client.id,  act, 'g-id_p-id', {'g-id_p-id': str(randint(1, 1000000000000000)),
                                          'time-id': datetime.now(),
                                          'shares': 0,
                                          'msg': text,
                                          'likes': 0},
                                          'production')
        
    elif act == 'comment':
        text = ' '.join(rw.random_words(count=randint(5, 100)))
        pub = client.components['g-id_p-id'][client.this_pub]
        db.make_interaction(client.id,  act, 'p-id_c-id', {'p-id_c-id': str(randint(1, 1000000000000000)),
                                            'g-id_p-id': pub,
                                            'time-id': datetime.now(),
                                            'msg': text},
                                            'production')

    elif act == 'like':
        pub = client.components['g-id_p-id'][client.this_pub]
        db.make_interaction(client.id, act, 'g-id_p-id', {'g-id_p-id': pub,
                                            'response': 'LIKE'},
                                            'consumption')
            
    elif act == 'unlike':
        pub = client.components['g-id_p-id'][client.this_pub]
        db.make_interaction(client.id, act, 'g-id_p-id', {'g-id_p-id': pub,
                                            'response': 'UNLIKE'},
                                            'consumption')
        
    elif act == 'scroll':
        pub = client.components['g-id_p-id'][client.this_pub]
        db.make_interaction(client.id, act, 'g-id_p-id', {'g-id_p-id': pub},
                                            'seen')
        
    elif act == 'follow':
        user_ids = client.components['u-id']
        if len(user_ids) > 0:
            user = choice(user_ids)
            db.make_interaction(client.id, act, 'u-id', {'u-id': user,},
                                                'Friendship')
        
    else:
        db.inst_action(client.id, act)

inter = {
    'comment' : {
        ('u-id', 'g-id', 'consumption') : [],
        ('u-id', 'p-id', 'consumption') : [],
        ('u-id', 'c-id', 'production') : ['time-id', 'msg'],
        ('u-id', 'r-id', 'production') : ['time-id', 'msg'],
        ('u-id', 'u-id', 'Friendship') : [],
        ('c-id', 'p-id', 'Belong') : [],
        ('p-id', 'g-id', 'Belong') : []
    },
    'like' : {
        ('u-id', 'g-id', 'consumption') : [],
        ('u-id', 'p-id', 'consumption') : [],
        ('u-id', 'c-id', 'production') : ['response'],
        ('u-id', 'r-id', 'production') : ['response'],
        ('c-id', 'p-id', 'Belong') : [],
        ('p-id', 'g-id', 'Belong') : []
    },
    'member' : {
        ('u-id', 'g-id', 'consumption') : ['url']
    },
    'post' : {
        ('u-id', 'g-id', 'consumption') : [],
        ('u-id', 'p-id', 'production') : ['time-id', 'shares', 'url', 'msg', 'likes'],
        ('p-id', 'g-id', 'Belong') : []
    }
}

inherited_inter = {
    'comment' : {
        ('u-id', 'g-id_p-id', 'consumption') : [],
        ('u-id', 'p-id_c-id', 'production') : ['time-id', 'msg'],
        ('p-id_c-id', 'g-id_p-id', 'Belong') : [],
        ('g-id_p-id', 'g-id', 'Belong') : []
    },
    'like' : {
        ('u-id', 'g-id_p-id', 'consumption') : [],
        ('u-id', 'p-id_c-id', 'production') : ['response'],
        ('p-id_c-id', 'g-id_p-id', 'Belong') : [],
        ('g-id_p-id', 'g-id', 'Belong') : []
    },
    'member' : {},
    'post' : {
        ('u-id', 'g-id_p-id', 'production') : ['time-id', 'shares', 'url', 'msg', 'likes'],
        ('g-id_p-id', 'g-id', 'Belong') : []
    }
}

atribs = {
    'comment' : {
        'c-id' : ['time-id', 'msg'],
        'u-id' : ['name']
    },
    'like' : {
        'u-id' : ['name']
    },
    'member' : {
        'u-id' : ['name', 'url']
    },
    'post' : {
        'p-id' : ['time-id', 'shares', 'url', 'msg', 'likes'],
        'u-id' : ['name']
    }
}

inherited_atribs = {
    'comment' : {
        'p-id_c-id' : ['time-id', 'msg', 'r-id'],
    },
    'like' : {},
    'member' : {},
    'post' : {
        'g-id_p-id' : ['time-id', 'shares', 'url', 'msg', 'likes'],
    }
}

def this_group(number):
    if number < 3: return 0
    elif number < 6: return 1
    else: return 2

db = DataBase2(url='data', detect_atrib=False, atribs=atribs, users_sign=['u-id'], detect_inter=False, inter=inter,
                detect_inherited_atrib=False, inherited_atribs=inherited_atribs,
                detect_inherited_inter=False, inherited_inter=inherited_inter)

clients = []
for key in db.users:
    for u in db.users[key]:
        client = Client(id=u.id, args=u.args)
        client.set_actions()
        clients.append(client)
        rec_view = client.rec_view()
        recs = {}

        for id in rec_view:
            if id in db.users_sign:
                val = db.db_recommend(client.id, id, 'Friendship', rec_view[id])
                if not val is None:
                    if len(val) > 0 and isinstance(val[0], list): val = val[0]
                    recs[id] = val

            else:
                val = db.db_recommend(client.id, id, 'consumption', rec_view[id])
                if not val is None:
                    if len(val) > 0 and isinstance(val[0], list): val = val[0]
                    recs[id] = val

        client.show(recs)


for i in range(1000):

    for c in clients:
        if c.values_pub is None:
            pub = c.components['g-id_p-id'][c.this_pub]
            user, _ = db.take(c.id, db.users)
            content = one_item(db, 'g-id_p-id', pub, item_related(user, 'g-id_p-id'))
            
            while not ('u-id', 'g-id_p-id') in db.similar_collab or not user.id in db.similar_collab[('u-id', 'g-id_p-id')] \
                or not pub in db.similar_collab[('u-id', 'g-id_p-id')][user.id]:
                time.sleep(10)
                print(f'waiting {pub} in user {user.id} collab')
            
            collab = db.similar_collab[('u-id', 'g-id_p-id')][user.id][pub]
            c.values_pub = (content, collab)

        if i >= 300 and c.rev:
            best = c.predict(c.save_recs)
            recommend = db.simulation(c.id, c.save_recs, 'g-id_p-id')

            if not best is None: c.counts[0][-1][this_group(best)] += 1
            
            if isinstance(recommend, int): c.counts[1][-1][this_group(recommend)] += 1
            c.cant_recs += 1

        c.rev = False
        c.save_recs = []
        act = c.do_something()
        client_actions(c, db, act)
        c.change_view(act)
        rec_view = c.rec_view()

        if act == 'init' or act == 'publish' or act == 'create_group' or act == 'follow' or act == 'include_group':
            c.rev = True
            recs = {}

            for id in rec_view:
                if id in db.users_sign:
                    val = db.db_recommend(c.id, id, 'Friendship', rec_view[id])
                elif id == 'g-id_p-id':
                    val = db.db_recommend(c.id, id, 'consumption', rec_view[id], 10)
                    c.save_recs = val
                else:
                    val = db.db_recommend(c.id, id, 'consumption', rec_view[id])
                if not val is None and len(val) > 0 and isinstance(val[0], list): val = val[0]
                recs[id] = val

            c.show(recs)
