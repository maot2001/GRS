from datetime import datetime
from pydantic import BaseModel

from utils import *


class User(BaseModel):
    id: str
    args: dict
    actions: dict = {}
    history: list = []
    productions: dict = {}
    consumptions: dict = {}
        
    def set_args(self, args: dict):
        self.args.update(args)

    def produce(self, id, production):
        if not id in self.productions: self.productions[id] = []
        if not production.id in self.productions[id]:
            self.productions[id].append(production.id)

    def consume(self, id, consumption):
        if not id in self.consumptions: self.consumptions[id] = []
        if not consumption.id in self.consumptions[id]:
            self.consumptions[id].append(consumption.id)

    def set_action(self, action: str):
        if not action in self.actions:
            self.actions[action] = [] 

    def inst_actions(self, action: str, *args):
        self.set_action(action)
        self.history.append(action)
        if args:
            self.actions[action].append((datetime.now(), args))
        else:
            self.actions[action].append(datetime.now())

    def number_actions(self):
        result = []
        for act in self.actions:
            if act == 'init' or act == 'close': continue
            for time in self.actions[act]:
                result.append(act)
        return result
    
    def __str__(self):
        msg = f'I am an User with id {self.id}'
        if len(self.args) > 0:
            msg += ' and my arguments are:\n'
            msg += '\n'.join([f'{key}: {self.args[key]}' for key in self.args])
        if len(self.history) > 0:
            msg += '\nThis is my stock history: '
            msg += ', '.join(self.history)
        return msg


class Item(BaseModel):
    id: str
    args: dict
    consumers: dict = {}
    producers: dict = {}

    def set_args(self, args):
        self.args.update(args)

    def set_consumer(self, id, consumer: User):
        if not id in self.consumers: self.consumers[id] = []
        if not consumer.id in self.consumers[id]:
            self.consumers[id].append(consumer.id)

    def set_producer(self, id, producer: User):
        if not id in self.producers: self.producers[id] = []
        if not producer.id in self.producers[id]:
            self.producers[id].append(producer.id)

    def __str__(self):
        msg = f'I am an Item with id {self.id}'

        if len(self.args) > 0:
            msg += ' and my arguments are:\n'
            msg += '\n'.join([f'{key}: {self.args[key]}' for key in self.args])
        else:
            msg += ' and I have no arguments\n'
    
        if len(self.producers) > 0:
            for key in self.producers:
                if len(self.producers[key]) > 20: continue
                msg += f'I have a producer that is of type {key} and its id is '
                msg += ', '.join([f'{u}' for u in self.producers[key]])
                msg += '\n'
        
        if len(self.consumers) > 0:
            for key in self.consumers:
                if len(self.consumers[key]) > 20: continue
                msg += f'I have a consumer that is of type {key} and its id is '
                msg += ', '.join([f'{u}' for u in self.consumers[key]])
                msg += '\n'
        return msg


class Consumption(BaseModel):
    user: User
    item: Item
    args: dict

    def set_args(self, args: dict):
        self.args.update(args)


class Production(BaseModel):
    user: User
    item: Item
    args: dict

    def set_args(self, args: dict):
        self.args.update(args)      


class User_Inter(BaseModel):
    info: str
    users: dict

    def __init__(self, info: str, data: dict, *args):
        super().__init__(info=info, users={})
        if not args == (None,):
            ids = tuple([u.id for u in args])
            self.users[ids] = data
    
    def add_inter(self, data: dict, *args):
        ids = tuple([i.id for i in args])
        if ids in self.users:
            self.users[ids] = data
        else:
            tmp = {ids : data}
            self.users.update(tmp)
               
    def similarity(self):
        pass               


class Item_Inter(BaseModel):
    info: str
    items: dict

    def __init__(self, info: str, data: dict, *args):
        super().__init__(info=info, items={})
        if not args == (None,):
            ids = tuple([i.id for i in args])
            self.items[ids] = data
    
    def add_inter(self, data: dict, *args):
        ids = tuple([i.id for i in args])
        if ids in self.items:
            self.items[ids] = data
        else:
            tmp = {ids : data}
            self.items.update(tmp)
               
    def similarity(self):
        pass
