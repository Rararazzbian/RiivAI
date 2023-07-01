import json

def run(action, username, trait=None):
    try:
        with open('usertraits.txt', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    if action == "get_traits":
        if username in data:
            return data[username]["traits"]
        else:
            return []

    elif action == "add_traits":
        if username not in data:
            data[username] = {"traits": []}
        data[username]["traits"].append(trait)

        with open('usertraits.txt', 'w') as file:
            json.dump(data, file, indent=4)

        print(f'Added the trait: "{trait}" to the user {username}')
        return "Trait added successfully."

    else:
        return "Invalid action."
