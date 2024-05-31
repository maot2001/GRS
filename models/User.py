import os

class User:
    def __init__(self, id, *args):
        self.id = id
        self.args = args

    def set_args(self, *args):
        self.args += args

    def create_inter(self):
        count = 0
        url = os.getcwd()
        while os.path.exists(os.path.join(url, 'models', f'User_Inter_{count}.py')):
            count += 1
        
        dict_form = '{kwargs.values() : args}'
        init_form = f'def __init__(self, info, *args, **kwargs):\n\t\tself.info = info\n\t\tself.users = {dict_form}'
        add_form = f'def add_inter(self, *args, **kwargs):\n\t\tif kwargs.values() in self.users:\n\t\t\tself.users[kwargs.values()] = args\n\t\telse:\n\t\t\ttmp = {dict_form}\n\t\t\tself.users.update(tmp)'
        text = f'class User_Inter:\n\t{init_form}\n\n\t{add_form}'
        with open(os.path.join(url, 'models', f'User_Inter_{count}.py'), 'w') as f:
            f.write(text)

        return count