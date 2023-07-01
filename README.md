# SoserAI
A Discord bot that uses OpenAI's GPT to generate responses and call external functions.

The bot uses the following environment variables:

- `OPENAI_API_KEY` for the OpenAI API key.
- `DISCORD_TOKEN` for the Discord bot token.
- `LLM_ENDPOINT` for the endpoint of the language model.
- `LLM_MODEL` for the name of the language model.
- `GOOGLESEARCH_API_KEY` for your google search API key.
- `GOOGLESEARCH_CSI_ID` for your google search CSI ID.

The bot connects to Discord using the `discord.py` library and listens for messages that mention it. When a message is received, the bot sends the message along with some extra information (such as message ID, channel ID, server ID, etc.) to the language model endpoint using the `requests` library.

The language model endpoint receives the message and the list of functions available in the plugins folder. It then generates a response using GPT and returns it as a JSON object. The bot parses the response and checks the finish reason. It will then either send the AI's message through Discord as a response, or call a function and repeat until it responds with an answer to the users original message.

The bot also keeps track of the messages by conversation ID and cleans them periodically to avoid exceeding the token limit.

## How to install

To install and run this bot, you need to have Python 3.11 or higher installed on your system. You also need to have an OpenAI API key and a Discord bot token.

To install the required libraries, run:

```bash
pip install -r requirements.txt
```

To set up the environment variables, modify the `example.env` file in the root folder of the project and modify the following lines to include your own:

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DISCORD_TOKEN=ODxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_ENDPOINT=https://api.openai.com/v1/chat/completions
LLM_MODEL=MODEL NAME (aka gpt-3.5-turbo-0613)
```

Replace the values with your own API key, bot token, language model endpoint and name.

To run the bot, run the Start.bat file included in the folder, the bot should soon print that it has connected to Discord and start listening for messages.

## How to create a plugin for SoserAI
To create a new plugin, follow these steps:

1. Create a JSON file with the same name as your plugin (e.g. `hello_world.json`) and add its metadata in it. The JSON file should have the following fields:

- `name`: The name of your plugin (e.g. `"google_search"`).
- `description`: A short description of what your plugin is for (e.g. `"Search the internet for a given query"`).
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

3. Create a new folder in the plugins folder with the name of your plugin (e.g. `google_search`).
4. Create a Python file with the same name as your plugin (e.g. `google_search.py`) and define your function in it. The function should accept arguments in the order of how they were listed in your plugins corresponding JSON file, and return a string output. Here's the included google_search plugin for example:

```python
from googlesearch import search
import googleapiclient.discovery
import os
from dotenv import load_dotenv

# Define the run function that takes a query and returns a string with the results
def run(prompt):
    GOOGLESEARCH_API_KEY = dot.getenv('GOOGLESEARCH_API_KEY')
    GOOGLESEARCH_CSE_ID = dot.getenv('GOOGLESEARCH_CSI_ID')
    try:
        service = googleapiclient.discovery.build("customsearch", "v1", developerKey=GOOGLESEARCH_API_KEY)
        response = service.cse().list(q=prompt, cx=GOOGLESEARCH_CSE_ID, num=5).execute()
        items = response.get("items", [])
        output = ""
        output += f"Found {len(items)} results for {prompt}\n"
        for item in items:
            output += item["title"] + "\n"
            output += item["link"] + "\n\n"
        return output
    except Exception as e:
        return str(e)
```

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
