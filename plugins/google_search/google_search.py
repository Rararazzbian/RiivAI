# Import the required modules
from googlesearch import search
import googleapiclient.discovery

# Define the run function that takes a query and returns a string with the results
def run(variables_list, prompt):
    print(variables_list)
    # Extract the desired variables from the variables_list
    data = {}
    for line in variables_list.strip().split("\n"):
        key, value = line.split(" = ")
        key = key.strip()
        value = value.strip("{}")
        data[key] = value
    
    # Access the variables you need
    GOOGLESEARCH_API_KEY = data.get("GOOGLESEARCH_API_KEY")
    GOOGLESEARCH_CSE_ID = data.get("GOOGLESEARCH_CSE_ID")
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
