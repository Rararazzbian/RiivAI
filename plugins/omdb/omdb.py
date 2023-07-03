from omdbapi.movie_search import GetMovie
import requests
from dotenv import load_dotenv
import os

load_dotenv()
apiKey = os.getenv('OMDB_API_KEY')

def run(action, title, season=None):
    if action == 'get_title':
        return get_title(title)

    elif action == 'list_episodes':
        return list_episodes(title, season)
    else:
        return 'Invalid action'

def get_title(title):
    #Fetch Movie Data with Full Plot 
    data_URL = 'http://www.omdbapi.com/?apikey=' + apiKey
    year = '' 
    params = {
        't':title,
        'y':year,
        'plot':'short'
    }
    response = requests.get(data_URL,params=params).json()
    return response

def list_episodes(title, season):
    url = "http://www.omdbapi.com/"
    params = {"t": title, "Season": season, "apikey": apiKey}

    response = requests.get(url, params=params)
    data = response.json()

    episodes_list = []

    episodes = data["Episodes"]
    for episode in episodes:
        episodes_list.append(f"{episode['Title']} (Episode {episode['Episode']}) - IMDb rating: {episode['imdbRating']}")
    return(episodes_list)
