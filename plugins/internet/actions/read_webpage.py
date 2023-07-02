import requests
from bs4 import BeautifulSoup
import re
import importlib
import os
from importlib import import_module

# Define the list of website domains and their associated function names
website_list = [
    {"website_domain": "www.furaffinity.net", "function_name": "furaffinity"},
    {"website_domain": "youtu.be", "function_name": "youtube"},
    {"website_domain": "www.youtube.com", "function_name": "youtube"},
    {"website_domain": "www.reddit.com", "function_name": "reddit"}
]

# Eka's plugin has been disabled as it isn't functional enough to be useful yet

def run(url):
    character_limit = 3000
    # Extract the domain from the given URL
    domain = url.split('/')[2]
    print(domain)
    
    # Find the associated function name based on the domain in the website list
    function_name = next((d["function_name"] for d in website_list if d["website_domain"] == domain), None)
    print(function_name)
    # Get the path of the action file
    action_path = os.path.join(f'plugins.internet.actions.sites.{function_name}')
    print(action_path)

    try:
        # Dynamically import the module
        action_module = import_module(action_path)
        
        # Call the run() function of the module and return its output
        return action_module.run(url)
    
    except ImportError as e:
        # Print the prompt if the module doesn't exist
        print(e)
        # Send a GET request to the website and store the response
        response = requests.get(url)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            # Parse the response content as HTML using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all the text elements in the HTML using the .text attribute
            text_elements = soup.text

            # Calculate the length of the text elements
            text_length = len(text_elements)

            # Check if the text length exceeds the character limit
            text_elements = text_elements.replace("""
""", "")
            if text_length > character_limit:
                # Cut off the text at the character limit
                text_elements = text_elements[:character_limit] + "\nThe rest of this website's text has been removed to fit within the token limit."
                print("Website has been shortened!")

            # Print the text length
            print(f"Total Characters: {text_length}")
            # Return the modified or original text elements
            return text_elements
        else:
            # Print an error message if the response status code is not 200
            return "Error: Unable to access the website"