import os
from importlib import import_module

def run(action, prompt):
    # Get the path of the action file
    action_path = os.path.join(f'plugins.internet.actions.{action}')
    
    # Dynamically import the module
    action_module = import_module(action_path)
    
    # Call the run() function of the module and return its output
    return action_module.run(prompt)
