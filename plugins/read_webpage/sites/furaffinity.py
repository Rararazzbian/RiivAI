from requests.cookies import RequestsCookieJar
import faapi
from faapi import FAAPI
from dotenv import load_dotenv
import os

FURAFFINITY_A_COOKIE = os.getenv('FURAFFINITY_A_COOKIE')
FURAFFINITY_B_COOKIE = os.getenv('FURAFFINITY_B_COOKIE')

cookies = RequestsCookieJar()
cookies.set("a", FURAFFINITY_A_COOKIE)
cookies.set("b", FURAFFINITY_B_COOKIE)

api = faapi.FAAPI(cookies)

def run(url):
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

def furaffinity_journal(journal_id):
    journal = api.journal(journal_id)
    journal_contents = f"""Title: {journal.title}
Author: {journal.author}
Journal Stats: {journal.stats}
Posted: {journal.date}
Journal Contents:
{journal.content}"""
    return journal_contents

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

def furaffinity_journals(username):
    # Get a User object
    user = api.user(username)

    # Get a list of JournalPartial objects, page 1
    journals, next_page = api.journals(username, page=1)
    journals_list = []
    journals_list.append(f'5 latest Journals from user {username}:')
    # Get up to 10 full Journal objects
    for journal in journals[:5]:
        # Get a Journal object
        full_journal = api.journal(journal.id)
        # Print or store the Journal object as you wish
        journals_list.append(f"""
Title: {full_journal.title}
Date: {full_journal.date}
Stats: {full_journal.stats}
Journal ID: {full_journal.id}
""")
    return journals_list
