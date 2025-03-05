import requests
import json

# API endpoint
API_URL = "http://localhost:8000/sources/"

# Sample data for the source database
source_data = {
    "name": "Test Database",
    "host": "",
    "port": 5432,
    "database": "",
    "user": "",
    "password": ""
}

# Convert data to JSON
json_data = json.dumps(source_data)

# Set headers for JSON content
headers = {
    "Content-Type": "application/json"
}

try:
    # Make the POST request
    response = requests.post(API_URL, data=json_data, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        print("Source database added successfully!")
        print("Response:", response.json())
    else:
        print(f"Error adding source database. Status code: {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")