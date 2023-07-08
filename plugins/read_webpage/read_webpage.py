import requests
from bs4 import BeautifulSoup
import re
import importlib
import os
from importlib import import_module
import json
import openai
import tiktoken

# Define the list of website domains and their associated function names
website_list = [
    {"website_domain": "www.furaffinity.net", "function_name": "furaffinity"},
    {"website_domain": "youtu.be", "function_name": "youtube"},
    {"website_domain": "www.youtube.com", "function_name": "youtube"},
    {"website_domain": "www.reddit.com", "function_name": "reddit"}
]

# Eka's plugin has been disabled as it isn't functional enough to be useful yet

openai.api_key = os.getenv('OPENAI_API_KEY')
SUMMARIZER_MODEL = os.getenv('WEB_SUMMARIZER_MODEL')

def summarize(prompt, question):
    if question:
        system_prompt = f"""Use the following webpage text to answer the following question: {question}
If an answer can't be made using the webpage, summarize the webpage instead."""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': prompt}]
        )
    else:
        system_prompt = f"""Use the following webpage text to answer the following question: {question}
If an answer can't be made using the webpage, summarize the webpage instead."""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{'role': 'system', 'content': 'Summarize the following webpage, including key details.'}, {'role': 'user', 'content': prompt}]
        )

    message = response["choices"][0]["message"]["content"]
    return message

def token_num(string: str) -> int:
    encoding_name = "cl100k_base"
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def run(url, question=None):
    if url.endswith(('.png', '.jpg', '.jpeg')):
        print('IMAGE DETECTED')
        image_content = f"""You requested to read an Image, your image recognition returned:
{read_image(url)}"""
        print(image_content)
        return image_content
    # Extract the domain from the given URL
    domain = url.split('/')[2]
    print(domain)
    token_limit = 10000
    chunk_limit = 2000
    # Find the associated function name based on the domain in the website list
    function_name = next((d["function_name"] for d in website_list if d["website_domain"] == domain), None)
    print(function_name)
    # Get the path of the action file
    action_path = os.path.join(f'plugins.read_webpage.sites.{function_name}')

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
            text_length = token_num(text_elements)

            # Check if the text length exceeds the character limit
            text_elements = text_elements.replace("""
""", "")
            if text_length > chunk_limit:
                if text_length > token_limit:
                    # Cut off the text at the character limit
                    text_elements = text_elements[:token_limit] + "\nThe rest of this website's text has been removed to fit within the token limit."
                    print("Website has been shortened!")
                    return summarize(text_elements, question)
                else:
                    return summarize(text_elements, question)
            else:
                # Print the text length
                print(f"Total Tokens: {token_num(text_elements)}")
                # Return the modified or original text elements
                return text_elements
        else:
            # Print an error message if the response status code is not 200
            return "Error: Unable to access the website"

def read_image(image_url):
    url = "https://api.imagga.com/v2/tags"
    querystring = {"image_url": image_url}

    headers = {
        "Authorization": "Basic YWNjXzQ2MmRiNGE5N2Q3MmYyNzo3OTY1OWI0YzIwYzVlODg0ODEzZWIxZDdjNWU1ZWQ3Zg=="
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    # Parse the response as a JSON object
    data = json.loads(response.text)

    # Get the list of tags from the result key
    tags = data["result"]["tags"]

    image_content = []

    # Loop through the first 10 tags and print them
    for i in range(10):
        tag = tags[i]
        image_content.append({'tag': tag["tag"]["en"], 'confidence': tag["confidence"]})
        
    return image_content
