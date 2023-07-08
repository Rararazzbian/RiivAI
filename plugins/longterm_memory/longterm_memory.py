import json
import random
import os

def run(action, server_id, memory=None):
    if action == "list_memories":
        # Check if usertraits.json exists
        if os.path.exists("longtermmemory.json"):
            # Read usertraits.json and list all traits for the specified user id
            with open("longtermmemory.json") as file:
                data = json.load(file)
            if server_id in data:
                traits = data[server_id]
                return traits
            else:
                return f"No memories found for server {server_id}."
        else:
            return f"No memories found for server {server_id}."
        
    elif action == "add_memory":
        # Add a trait to the user's traits list in usertraits.json
        with open("longtermmemory.json") as file:
            data = json.load(file)
        if server_id in data:
            traits = data[server_id]
        else:
            traits = []
        # Generate a unique 8-digit randomized trait ID
        memory_id = str(random.randint(10000000, 99999999))
        # Make sure the trait ID doesn't conflict with existing IDs
        while memory_id in [t.get("id") for t in traits]:
            trait_id = str(random.randint(10000000, 99999999))
        # Add the trait to the user's traits list
        traits.append({"id": memory_id, "memory": memory})
        # Update the usertraits.json file
        data[server_id] = traits
        with open("longtermmemory.json", "w") as outfile:
            json.dump(data, outfile)
        return f"Memory '{memory}' added successfully for server {server_id} with memory ID {memory_id}."
        
    elif action == "remove_memory":
        # Remove a trait from the user's traits list in usertraits.json
        with open("longtermmemory.json") as file:
            data = json.load(file)
        if server_id in data:
            traits = data[server_id]
            # Find the trait by ID and remove it
            traits = [t for t in traits if t.get("id") != memory]
            # Update the usertraits.json file
            data[server_id] = traits
            with open("longtermmemory.json", "w") as outfile:
                json.dump(data, outfile)
            return f"Memory '{memory}' removed successfully from server {server_id}."
        else:
            return f"No Memories found for server {server_id}."
        
    elif action == "reset_memories":
        # Remove the user completely from usertraits.json
        with open("longtermmemory.json") as file:
            data = json.load(file)
        if server_id in data:
            del data[server_id]
            with open("longtermmemory.json", "w") as outfile:
                json.dump(data, outfile)
            return f"Server memories for server {server_id} reset successfully."
        else:
            return f"No memories found for server {server_id}." 
    else:
        return "Invalid action. Please choose one of the following: get_memories, add_memory, remove_memory, reset_memories."
