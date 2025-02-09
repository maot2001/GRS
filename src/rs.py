from math import isnan
from random import sample
from threading import Thread
import time

from models import User
from utils import binary_search

class LRCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, key: int) -> int:
        if key in self.cache:
            # Mover el key a la última posición para marcarlo como usado
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return -1  # Retorna -1 si el key no está en el cache

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache[key] = value
            # Mover el key a la última posición para marcarlo como usado
            self.order.remove(key)
            self.order.append(key)
        else:
            if len(self.cache) >= self.capacity:
                # Elimina el menos recientemente usado
                oldest = self.order.pop(0)
                del self.cache[oldest]
            self.cache[key] = value
            self.order.append(key)


def user_related(db, user: User, id_group: str, id: str, motive: str):
    in_motive = set([user.id])

    for user_inter in db.user_inter:
        if ((id_group, id) == user_inter or (id, id_group) == user_inter):
            for rel in db.user_inter[user_inter]:
                if rel.info == motive:
                    for par in rel.users:
                        if par[0] == user.id:
                            in_motive.add(par[1])
                        elif par[1] == user.id:
                            in_motive.add(par[0])
                    break

    return sorted(in_motive)


def item_related(user: User, id: str):
    in_motive = set([])
    
    if id in user.consumptions:
        in_motive = in_motive.union(set(user.consumptions[id]))

    if id in user.productions:
        in_motive = in_motive.union(set(user.productions[id]))

    return sorted(in_motive)


def retrieval_exist(db, user: User, id_group: str, cache: LRCache, id: str, motive: str, outpout_dict: dict):
    if id in db.users:
        in_motive = cache.get('user_related')
        if in_motive == -1:
            in_motive = user_related(db, user, id_group, id, motive)
            cache.put('user_related', in_motive)

    else:
        in_motive = cache.get('item_related')
        if in_motive == -1:
            in_motive = item_related(user, id)
            cache.put('item_related', in_motive)

    for key in list(outpout_dict.keys()):
        pos = binary_search(in_motive, key)
        if pos > -1 and in_motive[pos] == key:
            outpout_dict.pop(key)

        
def score_triangle(db, user: User, id_group: str, cache: LRCache, id: str, motive: str, outpout_dict: dict):
    if id in db.users:
        in_motive = cache.get('user_related')
        if in_motive == -1:
            in_motive = user_related(db, user, id_group, id, motive)
            cache.put('user_related', in_motive)
            
            
        for user_inter in db.user_inter:
            if (id_group, id) == user_inter or (id, id_group) == user_inter:
                for rel in db.user_inter[user_inter]:
                    if rel.info == motive:
                        for u in in_motive:
                            if u == user.id: continue
                            for par in rel.users:
                                if par[0] == u and not par[1] in in_motive:
                                    outpout_dict[par[1]] += 1
                                elif par[1] == u and not par[0] in in_motive:
                                    outpout_dict[par[0]] += 1

    else:
        for user_inter in db.user_inter:
            if (id_group == user_inter[0] or id_group == user_inter[1]):
                for rel in db.user_inter[user_inter]:
                    for par in rel.users:
                        if par[0] == user.id:
                            other_user = db.take(par[1], db.users, user_inter[1])

                            if id in other_user.consumptions:
                                for i in other_user.consumptions[id]:
                                    if not i in outpout_dict: continue
                                    outpout_dict[i] += 1

                            if id in other_user.productions:
                                for i in other_user.productions[id]:
                                    if not i in outpout_dict: continue
                                    outpout_dict[i] += 1

                        elif par[1] == user.id:
                            other_user = db.take(par[0], db.users, user_inter[0])

                            if id in other_user.consumptions:
                                for i in other_user.consumptions[id]:
                                    if not i in outpout_dict: continue
                                    outpout_dict[i] += 1

                            if id in other_user.productions:
                                for i in other_user.productions[id]:
                                    if not i in outpout_dict: continue
                                    outpout_dict[i] += 1


def score_consume(db, user: User, id_group: str, cache: LRCache, id: str, motive: str, outpout_dict: dict):
    if id in db.users:
        for key in user.productions:
            for it in user.productions[key]:
                item = db.take(it, db.items, key)
                
                if id_group in item.consumers:
                    for u in item.consumers[id_group]:
                        if not u in outpout_dict: continue
                        outpout_dict[u] += 1


def score_produce(db, user: User, id_group: str, cache: LRCache, id: str, motive: str, outpout_dict: dict):
    if id in db.users:
        for key in user.consumptions:
            for it in user.consumptions[key]:
                item = db.take(it, db.items, key)

                if id_group in item.producers:
                    for u in item.producers[id_group]:
                        if not u in outpout_dict: continue
                        outpout_dict[u] += 1

    else:
        if id in user.consumptions:
            for it in user.consumptions[id]:
                item = db.take(it, db.items, id)
                
                if id_group in item.producers:
                    for u in item.producers[id_group]:
                        user = db.take(u, db.users, id_group)
                        
                        if id in user.productions:
                            for i in user.productions[id]:
                                if not i in outpout_dict: continue
                                outpout_dict[i] += 1


def score_co_consumer(db, user: User, id_group: str, cache: LRCache, id: str, motive: str, outpout_dict: dict):
    if id in db.users:
        for key in user.consumptions:
            for it in user.consumptions[key]:
                item = db.take(it, db.items, key)
                
                if id_group in item.consumers:
                    for u in item.consumers[id_group]:
                        if not u in outpout_dict: continue
                        outpout_dict[u] += 1

    else:
        if id in user.consumptions:
            for it in user.consumptions[id]:
                item = db.take(it, db.items, id)
                
                if id_group in item.consumers:
                    for u in item.consumers[id_group]:
                        user = db.take(u, db.users, id_group)
                        
                        if id in user.consumptions:
                            for i in user.consumptions[id]:
                                if not i in outpout_dict: continue
                                outpout_dict[i] += 1


def thread_collab(db, id_group: str, id: str, motive: str, retrievals: list, scores: list):
    try:
        time.sleep(3)
        if (id_group, id) in db.thread_collab:
            tmp = db.thread_collab[(id_group, id)]
            if tmp[0] == retrievals and tmp[1] == scores: return

        db.thread_collab[(id_group, id)] = (retrievals, scores)
        db.similar_collab[(id_group, id)] = {}
        
        while True:
            print(f'filter collaborative in {(id_group, id)} started')

            new_similar_collab = {}

            not_mod = db.users[id_group].copy()
            
            for user in not_mod:
                cache = LRCache(5)

                if id in db.users:
                    outpout_dict = {u.id: 0 for u in db.users[id]}
                else:
                    outpout_dict = {i.id: 0 for i in db.items[id]}

                for r in retrievals:
                    r(db, user, id_group, cache, id, motive, outpout_dict)

                if len(outpout_dict) > 0:
                    for s in scores:
                        s(db, user, id_group, cache, id, motive, outpout_dict)

                sorted_list = list(sorted(outpout_dict.items(), key=lambda item: item[1], reverse=True))

                if len(sorted_list) > 0:
                    max_val = max(1, sorted_list[0][1])
                    new_similar_collab[user.id] = {key[0]: (key[1]/max_val) for key in sorted_list}
                else: new_similar_collab[user.id] = []

            if (id_group, id) in db.thread_collab and db.thread_collab[(id_group, id)] != (retrievals, scores): break
            db.similar_collab[(id_group, id)] = new_similar_collab


            print(f'filter collaborative in {(id_group, id)} finished')
            time.sleep(300)
            if (id_group, id) in db.thread_collab and db.thread_collab[(id_group, id)] != (retrievals, scores): break

    except Exception as e:
        print(f'thread_collab error: {e} {type(e)}')


def one_item(db, id, item, in_motive):
    if len(in_motive) == 0: return 0
    
    count = 0

    vals = {}
    if id in db.similar_content and item in db.similar_content[id]:
        vals = db.similar_content[id][item]

    for i2 in in_motive:
        if i2 in vals:
            count += vals[i2]
        else:
            item1 = db.take(item, db.items, id)
            item2 = db.take(i2, db.items, id)
            try:
                val = db.thread_content[id](item1, item2)
            except:
                val = 0
            if isnan(val) or val is None: val = 0
            if not id in db.similar_content: db.similar_content[id] = {}
            if not item in db.similar_content[id]: db.similar_content[id][item] = {}
            if not i2 in db.similar_content[id]: db.similar_content[id][i2] = {}
            db.similar_content[id][item][i2] = val
            db.similar_content[id][i2][item] = val
            count += val

    return count/len(in_motive)

def mean_content(db, user: User, id_group: str, cache: LRCache, id: str, motive: str, outpout_dict: dict):
    if not id in db.thread_content:
        return outpout_dict.copy()
    
    content_dict = {}

    if id in db.users:
        in_motive = cache.get('user_related')
        if in_motive == -1:
            in_motive = user_related(db, user, id_group, id, motive)
            cache.put('user_related', in_motive)

        if not user.id in in_motive: in_motive.append(user.id)

        for u1 in outpout_dict:
            count = 0
            vals = {}
            if id in db.similar_content and u1 in db.similar_content[id]:
                vals = db.similar_content[id][u1]
            
            for u2 in in_motive:
                if u2 in vals:
                    count += vals[u2]
                else:
                    user1 = db.take(u1, db.users, id)
                    user2 = db.take(u2, db.users, id)
                    try:
                        val = db.thread_content[id](user1, user2)
                    except:
                        val = 0
                    if isnan(val) or val is None: val = 0
                    if not id in db.similar_content: db.similar_content[id] = {}
                    if not u1 in db.similar_content[id]: db.similar_content[id][u1] = {}
                    if not u2 in db.similar_content[id]: db.similar_content[id][u2] = {}
                    db.similar_content[id][u1][u2] = val
                    db.similar_content[id][u2][u1] = val
                    count += val

            content_dict[u1] = count/len(in_motive)

    else:
        in_motive = cache.get('item_related')
        if in_motive == -1:
            in_motive = item_related(user, id)
            cache.put('item_related', in_motive)

        if len(in_motive) == 0:
            return outpout_dict.copy()
        
        for i1 in outpout_dict:
            content_dict[i1] = one_item(db, id, i1, in_motive)

    return content_dict        


def recommend(db, user: str, id: str, motive: str, count: int, groups: int, retrievals: list, scores: list, proportion: tuple):
    try:
        user, id_group = db.take(user, db.users)
        cache = LRCache(5)
        
        if (not (id_group, id) in db.similar_collab or not user.id in db.similar_collab[(id_group, id)] \
            or db.thread_collab[(id_group, id)] != (retrievals, scores)):

            if id in db.users:
                outpout_dict = {u.id: 0 for u in db.users[id]}
            else:
                outpout_dict = {i.id: 0 for i in db.items[id]}

            for r in retrievals:
                r(db, user, id_group, cache, id, motive, outpout_dict)

            if len(outpout_dict) == 0: return []
    
            content_dict = mean_content(db, user, id_group, cache, id, motive, outpout_dict)

            for s in scores:
                s(db, user, id_group, cache, id, motive, outpout_dict)

            max_val = max(outpout_dict.values())
            max_val = max(max_val, 1)

            result_dict = {k: proportion[0]*content_dict[k] + proportion[1]*(outpout_dict[k]/max_val) for k in content_dict}
            if not (id_group, id) in db.similar_collab: db.similar_collab[(id_group, id)] = {}
            db.similar_collab[(id_group, id)][user.id] = result_dict.copy()

        else:
            new_outpout_dict = {k: 0 for k in db.similar_collab[(id_group, id)][user.id]}
            content_dict = mean_content(db, user, id_group, cache, id, motive, new_outpout_dict)
            result_dict = {k: proportion[0]*content_dict[k] + proportion[1]*db.similar_collab[(id_group, id)][user.id][k] for k in db.similar_collab[(id_group, id)][user.id]}


        Thread(target=thread_collab, args=(db, id_group, id, motive, retrievals, scores)).start()
        
        sorted_list = list(sorted(result_dict.items(), key=lambda item: item[1], reverse=True))
        
        if groups == 1:
            low = 0
            if len(sorted_list) >= count:
                low = round(sorted_list[count-1][1], 3)
                if low > sorted_list[count-1][1]: low -= 0.0005

            to_recommend = []

            for x in sorted_list:
                if x[1] < low: break
                to_recommend.append(x[0])

            if len(to_recommend) < count:
                return to_recommend
            
        else:
            size = len(sorted_list) // 3
            high = sorted_list[:size]
            medium = sorted_list[size+1:2*size]
            low = sorted_list[2*size+1:]

            high = [x[0] for x in high]
            medium = [x[0] for x in medium]
            low = [x[0] for x in low]

            high = [sample(high, count) for _ in range(3)]
            medium = [sample(medium, count) for _ in range(3)]
            low = [sample(low, count) for _ in range(4)]

            return high + medium + low

        return [sample(to_recommend, count) for _ in range(groups)]

    except Exception as e:
        print(f'recommend error: {e}')