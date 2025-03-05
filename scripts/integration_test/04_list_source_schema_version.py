import requests
from _config import BASE_URL

def list_schema_versions(source_id):
    """List all schema versions for a source database"""
    url = f"{BASE_URL}/sources/{source_id}/schema/versions"
    
    try:
        print(f"Listing schema versions for source ID {source_id}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            print("Successfully fetched schema versions!")
            return response.json()
        else:
            print(f"Error listing schema versions. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
if __name__ == "__main__":
    versions = list_schema_versions(1)
    if versions:
        print("\nSchema versions:")
        for version in versions:
            current = "[CURRENT]" if version.get("is_current") else ""
            print(f"Version {version.get('version'):<2} {current:<9} - Created at: {version.get('created_at')}")