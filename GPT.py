# Import the required libraries
from datetime import datetime
import json
import time
import requests
import importlib.util
import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import tracemalloc

# Start tracemalloc (for optimization)
tracemalloc.start()

# Grab the environment variables for the bot
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
FUNCTIONS_ENABLED = os.getenv('FUNCTIONS_ENABLED')
LLM_ENDPOINT = os.getenv('LLM_ENDPOINT')
LLM_MODEL = os.getenv('LLM_MODEL')

# Define the Discord intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Define the bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Print when the Discord bot has connected
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

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
        return function(**arguments)
    except Exception as e:
        #If an error occurs, return an error instead
        function_error = str(e)
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

# Define a function to clean the list of messages by conversation ID and message limit
def clean_list(conversation_id, message_limit):
    # Check if the conversation ID exists in the dictionary
    if conversation_id in messages_dict:
        # Get the list of messages
        messages = messages_dict[conversation_id]
        # Check if the total number of messages exceeds the limit
        if len(messages) > message_limit:
            # Calculate the number of messages to remove
            num_removed = len(messages) - message_limit
            messages = messages[-message_limit:]  # Keep only the most recent messages
            print(f"Removed {num_removed} messages from context.")
            messages_dict[conversation_id] = messages

async def ai_reply(input, message, conversation_id, info):
    # Add the input arg to the list of messages and then clean the list (removes the oldest messages)
    add_msg(conversation_id, input)
    clean_list(conversation_id, 7)
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
                # Sends an error in case of an exception
                send_message(f"It seems that {bot.user.name} has encountered an error!\n{response.text}", message)
        else:
            send_message(f"It seems that {bot.user.name} has encountered an error!\n{response.text}", message)
    except KeyError:
        send_message(f"It seems that {bot.user.name} has encountered an error!\n{response.text}", message)
    except KeyError:
        send_message(f"It seems that {bot.user.name} has encountered an error!\n{response.text}", message)
    if "error" in response_dict and "message" in response_dict["error"]:
        error_message = response_dict["error"]["message"]
        send_message(f"It seems that {bot.user.name} has encountered an error!\n{error_message}", message)

    try:
        choice = response_dict["choices"]
        if choice:
            # Check the finish reason
            finish_reason = choice[0]["finish_reason"]
            if finish_reason == "stop":
                # Take the AI's response and send that through Discord
                ai_response = response_dict["choices"][0]["message"]["content"]
                add_msg(conversation_id, {"role": "assistant", "content": f"{ai_response}"})
                await send_message(ai_response, message)
                print()
                print(ai_response)
                # Print token usage
                prompt_tokens = response_dict["usage"]["prompt_tokens"]
                completion_tokens = response_dict["usage"]["completion_tokens"]
                total_tokens = response_dict["usage"]["total_tokens"]
                print(f"Prompt Tokens: {prompt_tokens}")
                print(f"Completion Tokens: {completion_tokens}")
                print(f"Total Tokens: {total_tokens}")
            elif finish_reason == "function_call":
                # Take the function details and call it
                func_name = response_dict["choices"][0]["message"]["function_call"]["name"]
                func_args = response_dict["choices"][0]["message"]["function_call"]["arguments"]
                print(f"""Calling function `{func_name}` with the arguments:
                      {func_args}""")
                # Send the functions response back to the AI for another response
                parsed_argument = json.loads(func_args)
                function_response = run_function(func_name,parsed_argument)
                await ai_reply({"role": "function", "name": f"{func_name}", "content": f"{function_response}"}, message, conversation_id, info)
            else:
                # Handle other cases
                print("Unexpected finish reason!")
        else:
            error_msg = response_dict["error"]["message"]
            await send_message(f"***{bot.user.name} has encountered an error!***\n\n{error_msg}", message)
    except KeyError:
        error_msg = response_dict["error"]["message"]
        await send_message(f"***{bot.user.name} has encountered an error!***\n\n{error_msg}", message)


### DISCORD STUFF

# Define a function which sends an animated typing message through Discord
async def send_message(message, message_obj):
    # Define the size of the messages individual chunks
    size = 48
    # Send the first size characters of the message
    msg = await message_obj.channel.send(message[:size])
    # Index of the next character
    i = size
    # Loop until the end of the string plus size
    while i < len(message) + size:
        # Edit the message with the current substring
        await msg.edit(content=message[:i])
        # Increment the index by size
        i += size
        # Wait for a short time before repeating for the next chunk
        await asyncio.sleep(0.2)

# Define  a function which creates a "Bot is typing..." indicator in the Discord channel
async def TriggerTyping(secs, message):
    async with message.channel.typing():
        await asyncio.sleep(secs)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        # If the message came from the bot, ignore it
        return
    if f'<@{bot.user.id}>' in message.content:
        # If the message received contains a ping to the bot (@Bot), strip the ping from the message before continuing
        content = message.content.replace(f'<@{bot.user.id}>', '').lstrip()
        # Append the users name to the start of the message
        content = f"{message.author.name}: {content}"
        # Trigger the typing indicator
        await TriggerTyping(1, message)
        # Get the channel ID of the message which will become the Conversation ID
        channel = message.channel.id
        conversation_id = message.channel.id
        # Print the users message
        print()
        print(f'{content}')
        # Define some extra info which will be sent to the AI for additional context
        info = f"""

Current message context:
Message ID: "{message.id}"
Message Author: "{message.author.name}"
Message Author's Traits: {run_function("user_traits", {"action": "get_traits", "username": message.author.name})}
Message Author User ID: "{message.author.id}"
Message origins: From channel "{message.channel.name}" in server "{message.guild.name}"
Channel ID: "{message.channel.id}"
Server ID: "{message.guild.id}"
"""
        # Send the users message to the AI, alongside the conversation ID and info
        await ai_reply(({"role": "user", "content": content}), message, conversation_id, info)

# Run the Discord Bot
bot.run(DISCORD_TOKEN)
