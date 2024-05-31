import os
import importlib

files = [file[:-3] for file in os.listdir('models') if file.endswith('.py')]
models, models_index = [], {}

for file in files:
    models.append(importlib.import_module(f'models.{file}'))
    models_index[file] = len(models) - 1

mochila = models[models_index['Item']].Item(1, 'Mochila', 43)
marco = models[models_index['User']].User(1, 'Marco', 22, 'male')
consumption = models[models_index['Consumption']].Consumption(marco, 'good', 10, item1=mochila)
production = models[models_index['Production']].Production(marco, 'good', 10, '2020-12-16', item1=mochila)

zapato = models[models_index['Item']].Item(2, 'Zapato', 30)
count = mochila.create_inter()
models.append(importlib.import_module(f'models.Item_Inter_{count}'))
models_index[f'Item_Inter_{count}'] = len(models) - 1
content = models[models_index[f'Item_Inter_{count}']].Item_Inter('wanted for marco', True, 20, 'pepe', item1=mochila, item2=zapato)
for e in content.items:
    for i in e:
        print(i.id)
        print(i.args)

pepe = models[models_index['User']].User(2, 'Pepe', 20, 'male')
count = marco.create_inter()
models.append(importlib.import_module(f'models.User_Inter_{count}'))
models_index[f'User_Inter_{count}'] = len(models) - 1
collaborative = models[models_index[f'User_Inter_{count}']].User_Inter('brothers', True, 20, item1=marco, item2=pepe)
for e in collaborative.users:
    for i in e:
        print(i.id)
        print(i.args)