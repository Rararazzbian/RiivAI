# Import the FAAPI library and RequestsCookieJar
import faapi
from requests.cookies import RequestsCookieJar

# Create a cookie jar object and set the cookies a and b
cookies = RequestsCookieJar()
cookies.set("a", "FURAFFINITY_A_COOKIE")
cookies.set("b", "FURAFFINITY_B_COOKIE")

# Create a FAAPI object with the cookies
api = faapi.FAAPI(cookies)

# Define a function that takes a username and returns their info as a paragraph
def run(username):
    print(username)
    # Try to get the user object for the username
    try:
        user = api.user(username)
    # If faapi.exceptions.NotFound is raised, return "ERROR"
    except faapi.exceptions.NotFound:
        return f"User {username} does not exist on Fur Affinity."
    # Check if the user exists
    if user:
        # Format the user's info as a paragraph
        info = f"User: {user.name}.\nThey joined Fur Affinity on {user.join_date}.\nTheir stats are: {user.stats}.\nTheir bio is:\n{user.profile}.\nTheir info is:\n{user.info}"
        # Return the info string
        return info
    else:
        # Return an error message if the user does not exist
        return f"User {username} does not exist on Fur Affinity."
