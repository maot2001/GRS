import os

class Item:
    def __init__(self, id, *args):
        self.id = id
        self.args = args

    def create_inter(self):
        count = 0
        url = os.getcwd()
        while os.path.exists(os.path.join(url, 'models', f'Item_Inter_{count}.py')):
            count += 1
        
        dict_form = '{kwargs.values() : args}'
        init_form = f'def __init__(self, info, same_type, *args, **kwargs):\n\t\tself.info = info\n\t\tself.same_type = same_type\n\t\tself.items = {dict_form}'
        add_form = f'def add_inter(self, *args, **kwargs):\n\t\tif kwargs.values() in self.items:\n\t\t\tself.items[kwargs.values()] = args\n\t\telse:\n\t\t\ttmp = {dict_form}\n\t\t\tself.items.extends(tmp)'
        text = f'class Item_Inter:\n\t{init_form}\n\n\t{add_form}'
        with open(os.path.join(url, 'models', f'Item_Inter_{count}.py'), 'w') as f:
            f.write(text)

        return count