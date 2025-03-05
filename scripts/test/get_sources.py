import requests

# API endpoint for getting all sources
API_URL = "http://localhost:8000/sources/"

try:
    # Make the GET request
    response = requests.get(API_URL)

    # Check the response status code
    if response.status_code == 200:
        print("Successfully retrieved source databases!")
        print("Response:", response.json())
    else:
        print(f"Error retrieving source databases. Status code: {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")