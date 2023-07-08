# RiivAI
A Discord bot that uses OpenAI's GPT to generate responses and call external functions.

This bot is primarily designed for fun conversation, not to be taken seriously. This is a project I have been working on in my free time so I cannot guarantee this will stay up to date as new versions of OpenAI or Discord's content are released.

The bot connects to Discord using the `discord.py` library and listens for messages that mention it. When a message is received, the bot sends the message along with some extra information (such as message ID, channel ID, server ID, etc.) to the language model endpoint using the `requests` library.

## Features
-Function calling to external modules 📢
-Long Term Memory for Key info, User Traits, and Nicknames 🧠
-Stable Diffusion Image Generation 🖼️
-(Limited) Internet Access 🔍
With refined access to the following websites:
FurAffinity
YouTube
Reddit (Can only read post titles)

Twitter capabilities are not possible without their paid API, if you ask the AI to read a twitter page, it will not be able to as Twitter will only respond with an error.

## Built in Function capabilities:
-Google Search
-Reading websites (with limited success)
-Reading FurAffinity pages such as User profiles, Journals, Posts, etc.
-Reading YouTube videos through a URL (Will not work if the video provided is inside a playlist)

The language model endpoint receives the message and the list of functions available in the plugins folder. It then generates a response using GPT and returns it as a JSON object. The bot parses the response and checks the finish reason. It will then either send the AI's message through Discord as a response, or call a function and repeat until it responds with an answer to the users original message.

The bot also keeps track of the messages by conversation ID and cleans them periodically to avoid exceeding the token limit.

## How to install

This bot has only been tested on Python 3.11.4, I cannot guarantee compatibility with other versions.
These steps are primarily for windows, I have also run this AI on a Raspberry Pi running a Debian Server OS, but the setup I've only done through Windows.
Clone this git repository using the following command:
```bash
git clone https://github.com/Rararazzbian/RiivAI.git
```

To install the required libraries, CD into the bot's directory with `cd RiivAI` using your terminal and run:
```bash
pip install -r requirements.txt
```

To set up the environment variables, modify the `example.env` file in the root folder of the project and modify the following lines to include your own:
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DISCORD_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_ENDPOINT=https://api.openai.com/v1/chat/completions
LOCAL_LLM_ENDPOINT=<LOCAL_CHAT_COMPLETIONS_ENDPOINT>
LLM_MODEL=gpt-3.5-turbo-0613
LOCAL_LLM_MODEL=<LOCAL_MODEL_NAME>
GOOGLESEARCH_API_KEY=<API_KEY>
GOOGLESEARCH_CSE_ID=<CSI_ID>
YOUTUBE_API_KEY=<YT_API_KEY>
FURAFFINITY_A_COOKIE=<FA_A_COOKIE>
FURAFFINITY_B_COOKIE=<FA_B_COOKIE>
OMDB_API_KEY=<OMDB_API_KEY>
SD_API_URL=<SD_API_URL>
```
The LLM endpoint should stay the same unless you are using an alternative AI LLM with an ***OpenAI compatible API***.
Same applies for the LLM Model, unless you are wanting to upgrade this to GPT-4, this should stay as a ***Function Compatible*** LLM Model name.

Go to the OpenAI Platform website at platform.openai.com and sign in with an OpenAI account.
Click your profile icon at the top-right corner of the page and select “View API Keys.”
Click “Create New Secret Key” to generate a new API key, you can paste this into the `example.env` file replacing `<YOUR OPENAI KEY>`.
A ***Paid*** OpenAI account is required to avoid rate limit errors.
Click “Billing” and select “Set up paid account.”
Enter your card information and such.

Go to the Discord Developer Portal at discordapp.com/developers/applications and log in to your account.
Click “New Application” to create a new bot token.
Give a name to the bot and click “Create.”
Click on the “Bot” tab and use the “Click to Reveal Token” or “Copy” button under your bot username, paste this into the `example.env` file replacing the `<YOUR DISCORD BOT TOKEN>`.

The rest of the variables should be self explanitory and easy tutorials are not hard to find.
After you have filled in all the variables, rename the `example.env` to `.env`

## Setting up the System Prompt for your bot
To setup the system prompt, create an `initial_prompt.txt` file in the root folder of the project and fill it with your initial prompt message, this will setup how your AI will behave, for example you could write:
```
You are RiivAI, an AI companion.
Lore:
Your backstory is blah blah blah, setup the lore of the character or whatever you would like, etc.
```

To run the bot, run the Start.bat file included in the folder, the bot should soon print that it has connected to Discord and start listening for messages.

## How to create a plugin for RiivAI
To create a new plugin, follow these steps:

Create a new folder in the plugins folder with the name of your plugin (e.g. `google_search`).
Make a Python file with the same name as your plugin (e.g. `google_search.py`) and define your function in it. The function should accept arguments in the order of how they were listed in your plugins corresponding JSON file, and return a string output. Here's the included google_search plugin for example:
```python
# Import the required modules
from googlesearch import search
import googleapiclient.discovery
from dotenv import load_dotenv
import os

# Define the run function that takes a query and returns a string with the results
def run(prompt):
    GOOGLESEARCH_API_KEY = os.getenv('GOOGLESEARCH_API_KEY')
    GOOGLESEARCH_CSE_ID = os.getenv('GOOGLESEARCH_CSE_ID')
    # Create a service object using the API key and the CSE ID
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=GOOGLESEARCH_API_KEY)
    # Execute the search request and get the response
    response = service.cse().list(q=prompt, cx=GOOGLESEARCH_CSE_ID, num=5).execute()
    # Extract the list of items from the response
    items = response.get("items", [])
    # Initialize an empty string to store the output
    output = ""
    # Add the number of results found to the output
    output += f"Found {len(items)} results for {prompt}\n"
    # Loop through the items and add their titles and URLs to the output
    for item in items:
        output += item["title"] + "\n"
        output += item["link"] + "\n\n"
    # Return the output string
    return output
```

Create a JSON file with the same name as your plugin (e.g. `hello_world.json`) and add its metadata in it. The JSON file should have the following fields:
- `name`: The name of your plugin (e.g. `google_search`).
- `description`: A short description of what your plugin is for (e.g. `Search the internet for a given query`).
- `parameters`: A list of parameters that your plugin accepts, each with a name, type and description (e.g. `[{"name": "prompt", "type": "string", "description": "Your search query"}]`).

For example:
```json
{
  "name": "google_search",
  "description": "Search the internet for a given query",
  "parameters": {
    "type": "object",
    "properties": {
      "prompt": {
        "name": "prompt",
        "type": "string",
        "description": "Your search query"
      }
    }
  }
}
```

2. Save your files and restart the bot. Your plugin should be available for the bot to use.

To call your plugin from the bot, you can simply ask the bot to call the function.
The bot will parse your message and send it to the language model endpoint, which will return a function call request with the name and arguments of your plugin. The bot will then import and run your plugin and send its output back to the language model endpoint for another response. For example, you could write:
`Can you search for the latest Discord API Docs and provide a link?`

The bot will try to find a plugin that can perform this task (in this case being google_search) and send a function call request with the appropriate name and arguments. In this case, it will likely use the included google_search plugin and respond with:

```json
{
  "id": "chatcmpl-123",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": null,
      "function_call": {
        "name": "google_search",
        "arguments": "{ \"prompt\": \"Discord API Docs link\"}"
      }
    },
    "finish_reason": "function_call"
  }]
}
```
