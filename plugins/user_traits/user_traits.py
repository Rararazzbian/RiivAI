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

        trait_data = {"trait": trait}
        data[username]["traits"].append(trait_data)

        with open('usertraits.txt', 'w') as file:
            json.dump(data, file, indent=4)

        trait_id = len(data[username]["traits"])  # Assign the trait ID based on the length of the traits list
        print(f'Added the trait "{trait}" with ID {trait_id} to the user {username}')
        return "Trait added successfully."

    elif action == "remove_trait":
        if username in data:
            traits = data[username]["traits"]
            trait_found = False

            for trait_data in traits:
                if trait_data["id"] == trait:
                    traits.remove(trait_data)
                    trait_found = True
                    break

            if trait_found:
                # Update the IDs of the remaining traits
                for i, trait_data in enumerate(traits):
                    trait_data["id"] = i + 1

                with open('usertraits.txt', 'w') as file:
                    json.dump(data, file, indent=4)

                print(f'Removed the trait with ID {trait} from the user {username}')
                return "Trait removed successfully."
            else:
                return "Trait not found for the given ID."

        return "User not found."

    elif action == "reset_traits":
        if username in data:
            del data[username]
            with open('usertraits.txt', 'w') as file:
                json.dump(data, file, indent=4)
            print(f'All traits for the user {username} have been reset.')
            return "Traits reset successfully."

        return "User not found."

    else:
        return "Invalid action."
