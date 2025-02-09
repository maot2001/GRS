from models import *
from ia_acces import llama_acces

actions = ['init', 'finish', 'config', 'create_group', 'include_group' 'search', 'my_profile', 'other_profile', 'notifications', 'modify', 'photo', 'publish', 'comment', 'reaction']

def get_atribs(url: str, atribs: dict = {}, count = 1):
    """
    It is responsible for determining which attributes correspond to each id that belongs to a non-inherited key.

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

            msg += 'Tell me what id the attributes without id belong to, besides time-id if found, I only want the ids that represent a non-inherited key, also keep in mind that I only want attributes that relate to a single id, but these attributes can correspond to another id in another file, for example time-id is very dependent on the name of the file it is in, return them in the following format:\n{"a-id": ["a_val", "name"],\n"d-id": [],\n"c-id": ["time-id"]}\nIt is very important that you put the curly braces when answering {}'

            response = None
            while response is None:
                response = llama_acces(msg)
                    
            this_atribs[name_data[:-4]] = response.copy()

        responses.append(this_atribs)

    if count == 1:
        responses = responses[0]
    return responses

def get_users_sign(url: str, count = 1):
    """
    It is responsible for determining which id corresponds to the users.

    Args:
        url: root address of the database.
        count: number of times the query is to be performed, which allows the LLM's capacity to be tested.

    Returns:
        list: if count is 1, only the response dict is returned in type dict;
              if it is greater than 1, the list containing the response dicts is returned.
    """

    with open(os.path.join(url, 'atrib.txt'), 'r', encoding='utf-8') as f:
        atrib = f.read()

    msg = f'With this descriptions:\n{atrib}'
    msg += 'What are the IDs associated with users? There may be several. Return them in the following format:\n{"id": ["b-id", "a-id"]}\nIt is very important that you place the curly braces when answering {}'
    
    responses = []
    for _ in range(count):
        response = None
        while response is None:
            response = llama_acces(msg)

        responses.append(response['id'])

    if count == 1:
        responses = responses[0]

    return responses

def get_inter(url: str, users_sign: list = [], inter: dict = {}, count = 1):
    """
    It is responsible for determining which attributes correspond to each interrelation between objects that belong to
    non-inherited keys.

    Args:
        url: root address of the database.
        users_sign: list of ids that correspond to users.
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

    for _ in range(count):
        this_inter = inter.copy()
        
        for name_data in os.listdir(url):
            if not name_data.endswith('.csv'): continue
            if name_data[:-4] in this_inter: continue
            
            data = pd.read_csv(os.path.join(url, name_data))
            
            elements = []
            for col in data.head():
                elements.append(col)

            msg = f'In a file named "{name_data[:-4]}" there are these elements with their descriptions:\n'
                
            for atrib in txt_atribs:
                if atrib in elements:
                    msg += f'{atrib}{txt_atribs[atrib]}\n'

            msg += 'What are the interrelationships that exist between the ids that represent non-inherited objects? Associate the attributes that you consider relevant to each interrelation, whether they are ids or not.\nThe user ids are the following: '
            msg += ', '.join(users_sign)
            msg += '\nFor the interrelationships between users and objects, define whether the user produces the object or consumes it with the keywords "production" and "consumption". In the case of an interrelationship between users or an interrelationship between objects, define it with a name that starts with a capital letter.\nReturn them in the following format:\n{"(a-id, b-id, consumption)": ["c-id", "name"]\n"(a-id, c-id, production)": []\n"(b-id, c-id, Belong)": ["timeStamp"]}\nIt is very important that you put the braces when answering {}'

            response = None
            while response is None:
                response = llama_acces(msg)

            this_inter[name_data[:-4]] = response.copy()

        responses.append(this_inter)
                    

    if count == 1:
        responses = responses[0]

    return responses

def get_sim(url: str, atribs: list, types: dict):
    """
    It is responsible for determining which content-based filtering functions correspond to an object.

    Args:
        url: root address of the database.
        atribs: attributes that belong to the object.
        types: type of attributes that belong to the object.

    Returns:
        list: if count is 1, only the response dict is returned in type dict;
              if it is greater than 1, the list containing the response dicts is returned.
    """

    info = {}

    with open(os.path.join(url, 'atrib.txt'), 'r', encoding='utf-8') as f:
        atrib = f.read().split('\n')
        for text in atrib:
            ind = text.index(' ')
            if text[:ind] in atribs:
                info[text[:ind]] = text[ind:]

    text = 'I\'m doing content filtering on some objects for a recommendation system. I\'m going to give you the attributes they have and the type of each one, along with the description of what the attribute represents, so you can tell me if you can think of a similarity function that receives 2 elements of that type and returns a float value from 0 to 1. If you can\'t find the function, that\'s also an option, so stick with the option that\'s most valid for you. To access the attributes I\'m going to give you, you have to ask for the object\'s args attribute and put its name, this means that to access the "msg" attribute it would be a.args["msg"].\n\nThere is a class that has these attributes:\n'
    tmp = ''

    for a in atribs:
        text += f'{a}{info[a]}\n'
        tmp += f'{a} - {types[a]}\n'


    text += f'\nPlease note that objects may not have some of these attributes or have them with value None, check this before using any of them. I want you to return to me at the beginning of the text the name of the main function returns it in the following format:'
    text += '{"function" : "name_func"}\nThen I want the python code between ``` and ```.\nIt is very important that you put the braces and the quotes when answering {}```'

    response = None
    while response is None:
            response, code = llama_acces(text, True)

    return response['function'], code



def charge_database(db, url: str, detect_atrib: bool = True, atribs: dict[str, dict[str, list[str]]] = {}, 
                    users_sign: list[str] = [], detect_inter: bool = True,
                    inter: dict[str, dict[tuple[str, str, str], list[str]]] = {}, sim_content: dict[str, FunctionType] = {}):
    
    assert os.path.exists(url), 'The url does not exist'
    assert isinstance(detect_atrib, bool), 'detect_atrib must be a boolean'
    assert isinstance(detect_inter, bool), 'detect_inter must be a boolean'
    
    assert isinstance(atribs, dict), 'atribs in wrong type'
    assert all(isinstance(k, str) and isinstance(v, dict) and all(isinstance(k2, str) and isinstance(v2, list) \
            and all(isinstance(s, str) for s in v2) for k2, v2 in v.items()) for k, v in atribs.items()), 'atribs in wrong type'
    
    assert isinstance(users_sign, list) and all(isinstance(i, str) for i in users_sign), 'users_sign in wrong type'
    
    assert isinstance(inter, dict), 'inter in wrong type'
    assert all(isinstance(k, str) and isinstance(v, dict) and all(isinstance(k2, tuple) and len(k2) == 3 \
            and all(isinstance(i, str) for i in k2) and isinstance(v2, list) \
            and all(isinstance(j, str) for j in v2) for k2, v2 in v.items()) for k, v in inter.items()), 'inter in wrong type'
    
    assert isinstance(sim_content, dict), 'sim_content in wrong type'
    assert all(isinstance(k, str) and isinstance(v, FunctionType) for k, v in sim_content.items()), 'sim_content in wrong type'
    
    ids_all = set([])

    if detect_atrib:
        atribs = get_atribs(url, atribs)
        users_sign = get_users_sign(url)
    
    if detect_inter:
        inter = get_inter(url, users_sign, inter)

    for name_data in os.listdir(url):
        if not name_data.endswith('.csv'): continue
        this_inter = inter.get(name_data[:-4], {})
        this_args = atribs.get(name_data[:-4], {})

        data = pd.read_csv(os.path.join(url, name_data))

        # id selection
        ids = []
        for col in data.head():
            if col.endswith('-id') and col != 'time-id':
                ids.append(col)

        ids_all.update(ids)
        
        for i, row in data.iterrows():
            pos_user, pos_item = {}, {}

            for id in ids:
                the_id = id
                if id[-4].isdigit():
                    the_id = id[:-4] + id[-3:]

                try:
                    atr = this_args.get(id, [])
                    if id in users_sign:
                        pos_user[id], _ = db.create_user(the_id, clean(row, atr, id))

                    else:
                        pos_item[id], _ = db.create_item(the_id, clean(row, atr, id))
                except:
                    pass

            for var in this_inter:
                obj1, obj2 = None, None

                if var[0] == var[1]:
                    tmp1 = var[0]
                    tmp2 = var[1][:-3] + '2' + var[1][-3:]
                else:
                    tmp1 = var[0]
                    tmp2 = var[1]

                try:
                
                    if var[2] == 'consumption' or var[2] == 'production':
                        if tmp1 in pos_user and tmp2 in pos_item:
                            obj1 = db.users[var[0]][pos_user[tmp1]]
                            obj2 = db.items[var[1]][pos_item[tmp2]]

                        elif tmp1 in pos_item and tmp2 in pos_user:
                            obj1 = db.users[var[1]][pos_user[tmp2]]
                            obj2 = db.items[var[0]][pos_item[tmp1]]

                        if not obj1 is None and not obj2 is None:
                            try:
                                if var[2] == 'consumption':
                                    obj1.consume(var[1], obj2)
                                    obj2.set_consumer(var[0], obj1)
                                    db.create_interaction(clean(row, this_inter[var]), Consumption, db.consumptions, None, (var[0], var[1]), obj1, obj2)
                                else:
                                    obj1.produce(var[1], obj2)
                                    obj2.set_producer(var[0], obj1)
                                    db.create_interaction(clean(row, this_inter[var]), Production, db.productions, None, (var[0], var[1]), obj1, obj2)
                            except Exception as e:
                                print(e)

                    else:
                        user = True
                        if tmp1 in pos_user and tmp2 in pos_user:
                            obj1 = db.users[var[0]][pos_user[tmp1]]
                            obj2 = db.users[var[1]][pos_user[tmp2]]

                        elif tmp1 in pos_item and tmp2 in pos_item:
                            user = False
                            obj1 = db.items[var[0]][pos_item[tmp1]]
                            obj2 = db.items[var[1]][pos_item[tmp2]]

                        if not obj1 is None and not obj2 is None:
                            try:
                                pass
                                if user and obj1 != obj2:
                                    db.create_interaction(clean(row, this_inter[var]), User_Inter, db.user_inter, var[2], (var[0], var[1]), obj1, obj2)
                                else:
                                    db.create_interaction(clean(row, this_inter[var]), Item_Inter, db.item_inter, var[2], (var[0], var[1]), obj1, obj2)
                            except Exception as e:
                                print(e)
                
                except Exception as e:
                    print(e)
                
                pass

    db.set_merx(list(ids_all), atribs, users_sign, inter)
    db.set_sim_content(sim_content, url)
