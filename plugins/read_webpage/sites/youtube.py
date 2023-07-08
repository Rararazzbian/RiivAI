from pyyoutube import Api
from dotenv import load_dotenv
import os

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

def run(yt_link):
    # Create an API object with your API key
    api = Api(api_key=YOUTUBE_API_KEY)
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
    video_response = f"""Video title: {video_info.items[0].snippet.title}
Channel name: {video_info.items[0].snippet.channelTitle}
Likes: {video_info.items[0].statistics.likeCount}
Dislikes: {video_info.items[0].statistics.dislikeCount}
Description:
[{video_info.items[0].snippet.description}]"""
    return video_response
