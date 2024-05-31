import os
import importlib
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def similarity(args1, args2):
    sim = []
    for a in args1:
        if isinstance(a, dict) and isinstance(args2, dict):
            if set(a['genre']) & set(args2['genre']): sim.append('genre')
            
            tmp1 = [act['name'] for act in a['actor']]
            tmp2 = [act['name'] for act in args2['actor']]
            if set(tmp1) & set(tmp2): sim.append('actor')

            tmp1 = [act['name'] for act in a['director']]
            tmp2 = [act['name'] for act in args2['director']]
            if set(tmp1) & set(tmp2): sim.append('director')

            tmp1 = [act['name'] for act in a['creator']]
            tmp2 = [act['name'] for act in args2['creator']]
            if set(tmp1) & set(tmp2): sim.append('creator')
            
        if isinstance(a, list) and isinstance(args2, list):
            array1 = np.array(a).reshape(1, -1)
            array2 = np.array(args2).reshape(1, -1)
            if cosine_similarity(array1, array2)[0][0] > .8: sim.append('genome')

    if len(sim) > 0: return sim
    return None



files = [file[:-3] for file in os.listdir('models') if file.endswith('.py')]
models, models_index = [], {}

for file in files:
    models.append(importlib.import_module(f'models.{file}'))
    models_index[file] = len(models) - 1

items, users, consumptions, productions, item_inter, user_inter = [], [], [], [], [], []

for name_data in os.listdir('data'):
    with open(os.path.join('data', name_data), 'r', encoding='utf-8') as f:
        data = json.load(f)

    # LLM to identify which class the data goes into
    
    if 'movie' in name_data or 'genome' in name_data:
        for d in data:
            pos = -1
            created = False
            for i in range(len(items)):
                if items[i].id == d:
                    created = True
                    items[i].set_args(data[d])
                    pos = i
                    break

            if not created:
                items.append(models[models_index['Item']].Item(d, data[d]))
                pos = len(items) -1

            for item in items:
                if item.id == d: continue

                # LLM to define relationships between elements (if they are not explicitly defined, as is the current case) 
                # and generate interrelationships or add to existing ones

                relation = similarity(item.args, data[d])
                if relation:
                    for rel in relation:
                        created = False

                        for inter in item_inter:
                            if inter.info == rel:
                                created = True
                                inter.add_inter(item1=item, item2=items[pos])
                                break

                        if not created:
                            count = item.create_inter()
                            models.append(importlib.import_module(f'models.Item_Inter_{count}'))
                            models_index[f'Item_Inter_{count}'] = len(models) - 1
                            item_inter.append(models[models_index[f'Item_Inter_{count}']].Item_Inter(rel, True, item1=item, item2=items[pos]))

    else:
        for d in data:
            users.append(models[models_index['User']].User(d))

            # LLM to define relationships between elements (if they are not explicitly defined) 
            # and generate interrelationships or add to existing ones

            for e in data[d]:
                for item in items:
                    if e == item.id:
                        consumptions.append(models[models_index['Consumption']].Consumption(users[len(users)-1], None, data[d][e], item1=item))
                        break

print('Items:')
for e in items:
    print(e.id)
print()

print('Users:')
for e in users:
    print(e.id)
print()

print('Consumptions:')
for e in consumptions:
    print(f'{e.user.id}: {[i.id for i in e.items]}')
print()

print('Productions:')
for e in productions:
    print(f'{e.user.id}: {[i.id for i in e.items]}')
print()

print('Item_Inter:')
for e in item_inter:
    print(e.__class__)
    print(e.info)
    for ii in e.items:
        print(f'{[i.id for i in ii]}')
        print()
print()

print('User_Inter:')
for e in user_inter:
    print(e.__class__)
    print(e.info)
    for ui in e.users:
        print(f'{[i.id for i in ui]}')
        print()
print()

files = [f for f in os.listdir('models') if 'Inter' in f]
for file in files:
    os.remove(os.path.join('models', file))