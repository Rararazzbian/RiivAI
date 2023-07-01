import requests
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar
import faapi
from faapi import FAAPI
from pyyoutube import Api

# Define the list of website domains and their associated function names
website_list = [
    {"website_domain": "www.furaffinity.net", "function_name": "furaffinity"},
    {"website_domain": "youtu.be", "function_name": "youtube"},
    {"website_domain": "www.youtube.com", "function_name": "youtube"}
]

def run(url):
    character_limit = 3000
    
    # Extract the domain from the given URL
    domain = url.split('/')[2]
    print(domain)
    
    # Find the associated function name based on the domain in the website list
    function_name = next((d["function_name"] for d in website_list if d["website_domain"] == domain), None)

    # Check if a valid function name was found
    if function_name is not None:
        # Call the associated function dynamically
        result = globals()[function_name](url)
        return result
    else:
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

    

cookies = RequestsCookieJar()
cookies.set("a", "88c0bd8d-f196-4813-a0c6-f263e3af2740")
cookies.set("b", "5cf5e58d-ae7d-49e2-b4af-77084199c684")

api = faapi.FAAPI(cookies)

def furaffinity(url):
    # Extract the URL's first path
    first_path = url.split('/')[3]
    print(first_path)
    # Call the appropriate function based on the first path
    if first_path == "view":
        last_path = url.split("/")[-2]
        print(f"Last path: {last_path}")
        return furaffinity_view(last_path, "True")
    elif first_path == "user":
        last_path = url.split("/")[-2]
        print(f"Last path: {last_path}")
        return(furaffinity_user(last_path))
    elif first_path == "journal":
        last_path = url.split("/")[-2]
        print(f"Last path: {last_path}")
        return furaffinity_journal(last_path)
    elif first_path == "gallery":
        last_path = url.split("/")[-2]
        print(f"Last path: {last_path}")
        return furaffinity_gallery(last_path)
    elif first_path == "journals":
        last_path = url.split("/")[-2]
        print(f"Last path: {last_path}")
        return furaffinity_journals(last_path)
    else:
        return "Error: Invalid Furaffinity URL"

# Define the furaffinity_view function
def furaffinity_view(submission_id, show_author):
  # Create an FAAPI object with cookies
  # Get the submission object and the file bytes (not used)
  submission, file = api.submission(submission_id)
  # Create an empty dictionary to store the information
  info = {}
  # Store the title of the submission
  info["title"] = submission.title
  # Store the description of the submission
  info["description"] = submission.description
  # If show_author is true, store the author name and url
  if show_author:
    info["author"] = submission.author.name
    info["author_url"] = submission.author.url
  # Store the submission date
  info["date"] = submission.date
  # Return the info dictionary
  return info

def furaffinity_user(last_path):
    # Try to get the user object for the username
    try:
        user = api.user(last_path)
    # If faapi.exceptions.NotFound is raised, return "ERROR"
    except faapi.exceptions.NotFound:
        return f"User {last_path} does not exist on Fur Affinity."
    # Check if the user exists
    if user:
        # Format the user's info as a paragraph
        info = f"User: {last_path}.\nThey joined Fur Affinity on {user.join_date}.\nTheir stats are: {user.stats}.\nTheir bio is:\n{user.profile}.\nTheir info is:\n{user.info}"
        # Return the info string
        return info
    else:
        # Return an error message if the user does not exist
        return f"User {last_path} does not exist on Fur Affinity."

def furaffinity_gallery(username):
    # Get the first page of the user's gallery
    submissions, next_page = api.gallery(username)

    # Initialize an empty list to store the results
    results = []

    # Loop through the submissions, up to 10
    for submission in submissions[:5]:
        # Create a dictionary with the relevant information
        sub, sub_file = api.submission(submission.id, get_file=True)
        result = {
            "title": submission.title,
            "submission_url": f"https://www.furaffinity.net/view/{submission.id}",
            "image_url": f'{sub.file_url}',
            "stats": f'{sub.stats}'
        }

        # Append the dictionary to the results list
        results.append(result)

    # Return the results list
    return results

def youtube(yt_link):
    # Create an API object with your API key
    api = Api(api_key="AIzaSyCDHJnMWG6Wrgn20qL5P14MKX4dXvr-LVo")
    # check if the url is already just the video id
    if len(yt_link) == 11 and yt_link.isalnum():
        video_id = yt_link
    # check if the url is in the short format https://youtu.be/<video_id>
    elif yt_link.startswith("https://youtu.be/"):
        video_id = yt_link[17:]
    # check if the url is in the long format https://www.youtube.com/watch?v=<video_id>
    elif yt_link.startswith("https://www.youtube.com/watch?v="):
        video_id = yt_link[32:]
    # otherwise, return an error message
    else:
        print("Error!")
    # Define the video id

    # Get the video info using python-youtube
    video_info = api.get_video_by_id(video_id=video_id)

    # Print the video title, channel name, sub count, likes and dislikes, and description
    video_response = {
        "Video title:", video_info.items[0].snippet.title,
    "Channel name:", video_info.items[0].snippet.channelTitle,
    "Likes:", video_info.items[0].statistics.likeCount,
    "Dislikes:", video_info.items[0].statistics.dislikeCount,
    "Description:", video_info.items[0].snippet.description
    }
    return video_response
