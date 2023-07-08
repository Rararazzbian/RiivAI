import json
import random
import os

def run(action, user_id, trait=None):
    if action == "get_traits":
        # Check if usertraits.json exists
        if os.path.exists("usertraits.json"):
            # Read usertraits.json and list all traits for the specified user id
            with open("usertraits.json") as file:
                data = json.load(file)
            if user_id in data:
                traits = data[user_id]
                return traits
            else:
                return f"No traits found for user ID {user_id}."
        else:
            return f"No traits found for user ID {user_id}."
        
    elif action == "add_trait":
        # Add a trait to the user's traits list in usertraits.json
        with open("usertraits.json") as file:
            data = json.load(file)
        if user_id in data:
            traits = data[user_id]
        else:
            traits = []
        # Generate a unique 8-digit randomized trait ID
        trait_id = str(random.randint(10000000, 99999999))
        # Make sure the trait ID doesn't conflict with existing IDs
        while trait_id in [t.get("id") for t in traits]:
            trait_id = str(random.randint(10000000, 99999999))
        # Add the trait to the user's traits list
        traits.append({"id": trait_id, "trait": trait})
        # Update the usertraits.json file
        data[user_id] = traits
        with open("usertraits.json", "w") as outfile:
            json.dump(data, outfile)
        return f"Trait '{trait}' added successfully for user id {user_id} with trait ID {trait_id}."
        
    elif action == "remove_trait":
        # Remove a trait from the user's traits list in usertraits.json
        with open("usertraits.json") as file:
            data = json.load(file)
        if user_id in data:
            traits = data[user_id]
            # Find the trait by ID and remove it
            traits = [t for t in traits if t.get("id") != trait]
            # Update the usertraits.json file
            data[user_id] = traits
            with open("usertraits.json", "w") as outfile:
                json.dump(data, outfile)
            return f"Trait with ID '{trait}' removed successfully for user ID {user_id}."
        else:
            return f"No traits found for user {user_id}."
        
    elif action == "reset_traits":
        # Remove the user completely from usertraits.json
        with open("usertraits.json") as file:
            data = json.load(file)
        if user_id in data:
            del data[user_id]
            with open("usertraits.json", "w") as outfile:
                json.dump(data, outfile)
            return f"User ID {user_id} removed successfully from usertraits.json."
        else:
            return f"No traits found for user ID {user_id}."
        
    else:
        return "Invalid action. Please choose one of the following: get_traits, add_trait, remove_trait, reset_traits."
