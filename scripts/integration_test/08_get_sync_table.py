from typing import Dict, Any
from _config import BASE_URL
from _utils import print_sync_table
import requests

def get_sync_table(sync_table_id: int) -> Dict[str, Any]:
    """Get a specific sync table configuration"""
    
    url = f"{BASE_URL}/sync-tables/{sync_table_id}"
    
    print(f"Getting sync table with ID {sync_table_id}...")
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting sync table. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
if __name__ == "__main__":
    sync_table = get_sync_table(1)
    if sync_table:
        print_sync_table(sync_table)