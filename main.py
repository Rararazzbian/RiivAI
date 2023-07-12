# Import the required libraries
from datetime import datetime
import json
import time
import requests
import importlib.util
import os
import discord
from discord.ext import commands
from discord.ext import tasks
from discord import File
import asyncio
from dotenv import load_dotenv
import re
import urllib.request
import tempfile
import random

# Grab the environment variables for the bot
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LLM_ENDPOINT = os.getenv('LLM_ENDPOINT')
LLM_MODEL = os.getenv('LLM_MODEL')

# Define the Discord intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Define the bot
bot = commands.Bot(command_prefix='$', intents=intents)

# Print when the Discord bot has connected
@bot.event
async def on_ready():
    print(f'{bot.user.name} is alive!')
    bot.loop.create_task(check_channels())

@bot.command()
async def img(message_obj, *, message):
    if message_obj.message.attachments:
        print(message_obj.message.attachments[0].url)
        run_function("generate_image", {"prompt": message, "img_input": message_obj.message.attachments[0].url})
        with open('output.png', 'rb') as f:
            file = File(f)
            # Attach the local file to the message and send it through Discord
            await message_obj.channel.send(content=f'Generated image! "{message}"', file=file)
        os.remove('output.png')
    else:
        run_function("generate_image", {"prompt": message})
        with open('output.png', 'rb') as f:
            file = File(f)
            # Attach the local file to the message and send it through Discord
            await message_obj.channel.send(content=f'Generated image! "{message}"', file=file)
        os.remove('output.png')

# Define an empty functions dictionary
functions_list = []

# Set whether functions are enabled or not
FUNCTIONS_ENABLED=True

# Define a function which grabs the list of functions found in the plugins folder
def get_functions():
    if FUNCTIONS_ENABLED == True:
        plugins_folder = "plugins"
        functions = []
        # Repeats for every plugin found
        for root, dirs, files in os.walk(plugins_folder):
            for file in files:
                if file.endswith(".json"):
                    # Remove the .json extension
                    function_name = file[:-5]
                    file_path = os.path.join(root, file)
                    with open(file_path) as f:
                        function_data = json.load(f)
                        function_data["name"] = function_name
                        functions.append(function_data)
        # Return the full list of functions
        return functions
    else:
        # If functions are disabled, return an empty dictionary
        return []

# Define a function which accepts a function and its arguments and calls it
def run_function(function_name, arguments):
    plugin_path = f"plugins/{function_name}/{function_name}.py"
    spec = importlib.util.spec_from_file_location(function_name, plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, "run")
    try:
        # Try to call the function
        function_response = function(**arguments)
        return function_response
    except Exception as e:
        #If an error occurs, return an error instead
        function_error = str(e)
        print()
        print(f"Function error: {function_error}")
        return f"{function_name} returned an error: {function_error}"

# Global messages group
messages = []  

# Define a global dictionary to store lists of messages by conversation ID
messages_dict = {}

# Define a function to add a new message to the end of a list by conversation ID
def add_msg(conversation_id, message):
  # Check if the conversation ID exists in the dictionary
  if conversation_id in messages_dict:
    # Append the message to the existing list
    messages_dict[conversation_id].append(message)
  else:
    # Create a new list with the message and assign it to the conversation ID
    messages_dict[conversation_id] = [message]

# Define a function to get the list of messages by conversation ID
def get_msg(conversation_id, info):
    with open('initial_prompt.txt', 'r') as file:
        initial_prompt = file.read() + info
    # Check if the conversation ID exists in the dictionary
    if conversation_id in messages_dict:
        # Get the list of messages
        messages = messages_dict[conversation_id]
        # Remove the existing system message, if it exists
        messages = [msg for msg in messages if msg['role'] != 'system']
        # Insert the new initial_prompt variable as the first message in the list
        messages.insert(0, {'role': 'system', 'content': initial_prompt})
        # Return the list of messages
        return messages
    else:
        # Return an empty list
        return []

def clean_list(conversation_id, message_limit):
    if conversation_id in messages_dict:
        messages = messages_dict[conversation_id]
        cleaned_messages = []
        for message in messages:
            if message['role'] == 'function':
                message['content'] = 'This response has been removed to save tokens'
            cleaned_messages.append(message)
        messages_dict[conversation_id] = cleaned_messages[-message_limit:]

async def ai_reply(input, conversation_id, info, message=None):
    # Add the input arg to the list of messages and then clean the list (removes the oldest messages)
    add_msg(conversation_id, input)
    # Define the payload which will be sent to the AI
    payload = {
      "model": LLM_MODEL,
      "functions": get_functions(),
      "messages": get_msg(conversation_id, info)
    }
    # Define the authorization header for the API key
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(LLM_ENDPOINT, json=payload, headers=headers)
    response_dict = json.loads(response.text)
    try:
        choice = response_dict["choices"]
        if choice:
            # If "choices" exists in the AI's response, define the finish reason variable
            finish_reason = choice[0]["finish_reason"]
            if finish_reason:
                # Continue with further actions
                pass
            else:
                if message == None:
                    return f"It seems that {bot.user.name} has encountered an error! Check the output for details."
                else:
                    # Sends an error in case of an exception
                    await send_message(f"It seems that {bot.user.name} has encountered an error! Check the output for details.", message)
                    print(response.text)
        else:
            if message == None:
                    return f"It seems that {bot.user.name} has encountered an error! Check the output for details."
            else:
                await send_message(f"It seems that {bot.user.name} has encountered an error! Check the output for details.", message)
                print(response.text)
    except KeyError:
        if message == None:
            return f"It seems that {bot.user.name} has encountered an error! Check the output for details."
        else:
            await send_message(f"It seems that {bot.user.name} has encountered an error! Check the output for details.", message)
            print(response.text)

    try:
        choice = response_dict["choices"]
        if choice:
            # Check the finish reason
            finish_reason = choice[0]["finish_reason"]
            if finish_reason == "stop":
                # Take the AI's response and send that through Discord
                ai_response = response_dict["choices"][0]["message"]["content"]
                add_msg(conversation_id, {"role": "assistant", "content": f"{ai_response}"})
                # Print token usage
                prompt_tokens = response_dict["usage"]["prompt_tokens"]
                completion_tokens = response_dict["usage"]["completion_tokens"]
                print()
                print(bot.user.name + ' replied: ' + ai_response)
                print(f"Prompt Tokens: {prompt_tokens}")
                print(f"Completion Tokens: {completion_tokens}")
                # Clear out old messages and function outputs
                clean_list(conversation_id, 7)
                if message == None:
                    return ai_response
                else:
                    await send_message(ai_response, message)
            elif finish_reason == "function_call":
                # Take the function details and call it
                func_name = response_dict["choices"][0]["message"]["function_call"]["name"]
                func_args = response_dict["choices"][0]["message"]["function_call"]["arguments"]
                print()
                print(f"""Calling function `{func_name}` with the arguments:
                      {func_args}""")
                # Send the functions response back to the AI for another response
                parsed_argument = json.loads(func_args)
                function_response = run_function(func_name,parsed_argument)
                add_msg(conversation_id, {"role": "assistant", "content": "", "function_call": {"name": f"{func_name}", "arguments": f"{func_args}"}})
                await ai_reply({"role": "function", "name": f"{func_name}", "content": f"{function_response}"}, conversation_id, info, message)
            else:
                # Handle other cases
                print("Unexpected finish reason!")
        else:
            error_msg = response_dict["error"]["message"]
            if message == None:
                return f"***{bot.user.name} has encountered an error!***"
            else:
                await send_message(f"***{bot.user.name} has encountered an error!***", message)
            print(error_msg)
    except KeyError:
        error_msg = response_dict["error"]["message"]
        if message == None:
            return f"***{bot.user.name} has encountered an error!***"
        else:
            await send_message(f"***{bot.user.name} has encountered an error!***", message)
        print(error_msg)

async def send_message(message, message_obj):
    # Check if message contains an image url
    image_url_pattern = re.compile(r'(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png)')
    # Search for an image url in the message
    match = image_url_pattern.search(message)
    if match:
        # Check if the url starts with http://localstorage/
        if match.group().startswith('http://localstorage/'):
            # Replace the url with an empty string and append the local file path to it
            local_file_path = match.group().replace('http://localstorage/', '')
            local_file_path = os.path.join(os.getcwd(), local_file_path)
            message = image_url_pattern.sub('***Image***', message)
            # Open the local file as f
            with open(local_file_path, 'rb') as f:
                file = File(f)
                # Attach the local file to the message and send it through Discord
                await message_obj.channel.send(content=message, file=file)
            os.remove(local_file_path)
        else:
            # Download the image from the url and save it to a file
            response = requests.get(match.group())
            with open('image.jpg', 'wb') as f:
                f.write(response.content)
            # Strip the url from the message
            message = image_url_pattern.sub('***Image***', message)
            # Attach the downloaded image to the message and send it through Discord
            with open('image.jpg', 'rb') as f:
                file = File(f)
                await message_obj.channel.send(content=message, file=file)
            # Delete the downloaded image
            os.remove('image.jpg')
    else:
        # Send the message through Discord without any modifications
        await message_obj.channel.send(message)

# Define  a function which creates a "Bot is typing..." indicator in the Discord channel
async def TriggerTyping(secs, message):
    async with message.channel.typing():
        await asyncio.sleep(secs)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        # If the message came from the bot, ignore it
        return
    else:
        if message.content.startswith(bot.command_prefix):
            await bot.process_commands(message)
        else:
            if f'<@{bot.user.id}>' in message.content:
                # If the message received contains a ping to the bot (@Bot), strip the ping from the message before continuing
                content = message.content.replace(f'<@{bot.user.id}>', '').lstrip()
                # Set a nickname
                nickname = run_function("user_nickname", {'action': 'get_nickname', 'user_id': f'{message.author.id}', 'server_id': f'{message.guild.id}'})
                if nickname != f"No nickname found for user {message.author.id} in server {message.guild.id}":
                    # If a nickname is found, replace the users display name with the nickname
                    content = f"[Current Time: {datetime.now()}, Name: {nickname}]: {content}"
                else:
                    # If a nickname is not found, leave the message as is
                    content = f"[Current Time: {datetime.now()}, Name: {message.author.display_name}]: {content}"
                if len(message.attachments) > 0:
                    for file in message.attachments:
                        content = f"""{content}
        This message has a file attached with the URL: {file.url}"""
                # Trigger the typing indicator
                await TriggerTyping(1, message)
                # Get the channel ID of the message which will become the Conversation ID
                channel = message.channel.id
                conversation_id = message.channel.id
                # Print the users message
                print()
                print(f'{content}')
                # Grab all the custom emojis from the current server
                emojis = message.guild.emojis
                emoji_list = []
                for emoji in emojis:
                    # Append each emoji found to a list
                    emoji_list.append(f"<:{emoji.name}:{emoji.id}>")
                # Define some extra info which will be sent to the AI for additional context
                info = f"""

-Function calling for accessing external services
-Long Term Memory for User Traits and Nicknames 
-Stable Diffusion Image Generation 
-Internet Access

Twitter capabilities are not possible without their paid API, if you ask the AI to read a twitter page, it will not be able to as Twitter will only respond with an error.

Your responses are limited to a maximum of 1500 characters.

You have access to the following server emojis:
{emoji_list}

Current message context:
Message ID: "{message.id}"
Message Author: "{message.author.name}"
Message Author's Traits: {run_function("user_traits", {"action": "get_traits", "user_id": message.author.name})}
Message Author User ID: "{message.author.id}"
Message origins: From channel "{message.channel.name}" in server "{message.guild.name}"
Channel ID: "{message.channel.id}"
Server ID: "{message.guild.id}"
"""
                # Send the users message to the AI, alongside the conversation ID and info
                await ai_reply(({"role": "user", "content": content}), conversation_id, info, message)

async def check_channels():
    while True:
        wait_time = 15
        await bot.wait_until_ready()
        while not bot.is_closed():
            channels_to_check = [1072581164868583636]
            for channel_id in channels_to_check:
                channel = bot.get_channel(channel_id)
                async for message in channel.history(limit=1):
                    created_at_naive = message.created_at.replace(tzinfo=None)
                    time_difference = datetime.utcnow() - created_at_naive
                    if time_difference.seconds > wait_time * 60:
                        print('Inactivity detected!')
                        if random.random() < 0.05:
                            await channel.send(await ai_reply(({"role": "user", "content": f'[Current Time: {datetime.now()}]: Inactivity detected, try to spark a conversation about something vore related.'}), channel_id, '.', None))
                        else:
                            print(f'{bot.user.name} chose not to speak.')
            await asyncio.sleep(wait_time * 60)

# Run the Discord Bot
bot.run(DISCORD_TOKEN)
