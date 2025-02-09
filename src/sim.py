from ia_acces import llama_acces

def simulate(db, user, recommends, id, objetive):
    try:
        user, _ = db.take(user, db.users)

        msg = f'{user}\n\n'
        if len(user.productions) > 0:
            msg += 'I produce this Items:\n'
            for key in user.productions:
                msg += f'With this key {key}:\n'
                for i in user.productions[key]:
                    msg += f'{i}\n'
            
        if len(user.consumptions) > 0:
            msg += 'I consume this Items:\n'
            for key in user.consumptions:
                msg += f'With this key {key}:\n'
                for i in user.consumptions[key]:
                    msg += f'{i}\n'

        simple = False

        if isinstance(recommends[0], list):
            simple = True
            msg += f'And I want to know which of this group of recommendations will generate more reactions and what actions the user will take:\nWith this key {id}:\n'
            for i in range(len(recommends)):
                msg += f'{i}: [\n'
                for j in recommends[i]:
                    msg += f'{j}\n'
                msg += ']\n\n'
            msg += 'Associated with the "recommend" field I want the list between 0 and 9 that will generate the most reactions and associated with "actions" I want the sequence of actions that the user will execute next, the number of actions to predict is at most 20. The data to which you relate the actions has to belong to the list selected in "recommend". Return them in the following format:\n{\n"recommend": "17",\n"actions": ["search", "(comment, 117291968282998_1219477638064420)", "publish", "(reaction, 117291968282998_1219344994744351)"]\n}\n\nIt is important that you remember to put the {}'

        else:
            msg += f'And I want to know what actions the user will take when shown this group of recommendations:\nWith this key {id}:\n' 
            for key in recommends:
                msg += f'{key}\n'
            msg += '\nAssociated with the "actions" field I want the sequence of actions that the user will execute next, the number of actions to predict is at most 20. Return them in the following format:\n{\n"actions": ["search", "(comment, 117291968282998_1219477638064420)", "post", "(reaction, 117291968282998_1219344994744351)"]\n}\n\nIt is important that you remember to put the {}'

        response = None
        while response is None:
            response = llama_acces(msg)
            if simple and not response['recommend'].isdigit(): response = None
            else:
                if "search" == response['actions'][0] and "(comment, 117291968282998_1219477638064420)" == response['actions'][1]:
                    response['actions'].remove("search")
                    response['actions'].remove("(comment, 117291968282998_1219477638064420)")
                    if "publish" == response['actions'][0]:
                        response['actions'].remove("publish")
                        if "(reaction, 117291968282998_1219344994744351)" == response['actions'][0]:
                            response['actions'].remove("(reaction, 117291968282998_1219344994744351)")

                elif "(comment, 117291968282998_1219477638064420)" == response['actions'][1]:
                    response['actions'].remove("(comment, 117291968282998_1219477638064420)")
                    if "publish" == response['actions'][1]:
                        response['actions'].remove("publish")
                        if "(reaction, 117291968282998_1219344994744351)" == response['actions'][1]:
                            response['actions'].remove("(reaction, 117291968282998_1219344994744351)")

                if len(response['actions']) == 0: response = None

                for i in range(len(response['actions'])):
                    if ', ' in response['actions'][i]:
                        vals = response['actions'][i][1:-1].split(', ')
                        response['actions'][i] = (vals[0], vals[1])

                        if vals[1] == '':
                            response['actions'][i] = vals[0]
                            continue
                        
                        exist = False
                        if simple and vals[1] in recommends[int(response['recommend'])]:
                            exist = True
                        elif vals[1] in recommends:
                            exist = True

                        if not exist:
                            response = None
                            break
        
        if simple: return int(response['recommend'])
        return response['actions']
        
    except Exception as e:
        print(e)
        return []