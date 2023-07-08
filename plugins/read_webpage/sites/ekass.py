import requests
from bs4 import BeautifulSoup

def run(url):
    # Extract the URL's first path
    first_path = url.split('/')[3]
    print(first_path)
    # Call the appropriate function based on the first path
    if first_path == "g4":
        elements_to_find = ['div', {'class': 'g-box-contents'}, 'p']
        found_elements = extract_elements(url, elements_to_find)
        return found_elements

def extract_elements(url, elements_to_find):
    response = requests.get(url)
    html_content = response.text
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract the specified elements
    extracted_elements = []
    for element_to_find in elements_to_find:
        if isinstance(element_to_find, str):
            elements = soup.find_all(element_to_find)
        elif isinstance(element_to_find, dict):
            tag_name = list(element_to_find.keys())[0]
            attributes = element_to_find[tag_name]
            elements = soup.find_all(tag_name, attributes)
        else:
            raise ValueError('Invalid element specification')
        if elements:
            extracted_elements.append(elements[0])
    return extracted_elements
