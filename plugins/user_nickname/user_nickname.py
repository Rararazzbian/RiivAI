import json

def run(action, user_id=None, nickname=None, server_id=None):
    if action == 'add_nickname':
        nicknames = {}
        try:
            with open('nicknames.json', 'r') as f:
                nicknames = json.load(f)
        except FileNotFoundError:
            pass

        if server_id not in nicknames:
            nicknames[server_id] = {}

        nicknames[server_id][user_id] = nickname

        with open('nicknames.json', 'w') as f:
            json.dump(nicknames, f)

        return f'Nickname "{nickname}" added for user {user_id} in server {server_id}'

    elif action == 'get_nickname':
        try:
            with open('nicknames.json', 'r') as f:
                nicknames = json.load(f)
                return nicknames[server_id][user_id]
        except (FileNotFoundError, KeyError):
            return f'No nickname found for user {user_id} in server {server_id}'

    elif action == 'remove_nickname':
        try:
            with open('nicknames.json', 'r') as f:
                nicknames = json.load(f)
                del nicknames[server_id][user_id]
                with open('nicknames.json', 'w') as f:
                    json.dump(nicknames, f)
                return f'Nickname removed for user {user_id} in server {server_id}'
        except (FileNotFoundError, KeyError):
            return f'No nickname found for user {user_id} in server {server_id}'

    elif action == 'get_list':
        try:
            with open('nicknames.json', 'r') as f:
                nicknames = json.load(f)
                if server_id not in nicknames:
                    return f'None found.'
                else:
                    return nicknames[server_id]
        except FileNotFoundError:
            return {}
    else:
        return 'Invalid action'
