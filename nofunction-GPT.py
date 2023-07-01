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

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LLM_ENDPOINT = os.getenv('LLM_ENDPOINT')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

messages = []  # Global messages group

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
def get_msg(conversation_id):
    with open('initial_prompt.txt', 'r') as file:
        initial_prompt = file.read()
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

# Define a function to clean the list of messages by conversation ID and character limit
def clean_list(conversation_id, char_limit):
    # Check if the conversation ID exists in the dictionary
    if conversation_id in messages_dict:
        # Get the list of messages
        messages = messages_dict[conversation_id]
        # Calculate the total number of characters in the list
        total_chars = sum(len(msg["content"]) for msg in messages)
        print(f"Total conversation characters: {total_chars}")
        # Check if the total number of characters exceeds the limit
        if total_chars > char_limit:
            # Calculate the number of messages to remove
            num_removed = 0
            while total_chars > char_limit:
                msg = messages.pop(0)  # Remove the first message in the list
                total_chars -= len(msg["content"])  # Subtract its length from the total number of characters
                num_removed += 1
            print(f"Removed {num_removed} messages from context.")

async def ai_reply(input, conversation_id, message):
    add_msg(conversation_id, input)
    clean_list(conversation_id, 4000)
    print(get_msg(conversation_id))
    # Set up headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer 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',
    }
    # Set up data
    data = {
      "model": 'gpt-3.5-turbo-0613',
      "messages": get_msg(conversation_id)
    }
    # Send request
    response = requests.post('http://127.0.0.1:5001/v1/chat/completions', headers=headers, json=data)
    # Print response
    response_dict = json.loads(response.text)
    ai_response = response_dict["choices"][0]["message"]["content"]
    add_msg(conversation_id, {'role': 'user', 'content': ai_response})
    await send_message(ai_response, message)

async def TriggerTyping(secs, message, Typing):
    if Typing == True:
        async with message.channel.typing():
            await asyncio.sleep(secs)

async def send_message(message, message_obj):
    stringResponse = message # the message you want to type
    size = 48 # the size of each edit
    msg = await message_obj.channel.send(stringResponse[:size]) # send the first size characters of the message
    i = size # index of the next character
    while i < len(stringResponse) + size: # loop until the end of the string plus size
        await msg.edit(content=stringResponse[:i]) # edit the message with the current substring
        i += size # increment the index by size
        await asyncio.sleep(0.4) # wait for a short time

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if f'<@{bot.user.id}>' in message.content:
        content = message.content.replace(f'<@{bot.user.id}>', '').lstrip()
        content = f"{message.author.name}: {content}"
        Typing = True
        asyncio.create_task(TriggerTyping(1, message, Typing))
        conversation_id = message.channel.id
        channel = bot.get_channel(conversation_id)
        print()
        print(f'{content}')
        time.sleep(1)
        asyncio.create_task(ai_reply(({"role": "user", "content": content}), conversation_id, message))

bot.run(DISCORD_TOKEN)
