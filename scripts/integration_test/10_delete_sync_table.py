from typing import Dict, Any, List, Optional
from _config import BASE_URL
import requests

def delete_sync_table(sync_table_id: int) -> bool:
    """Delete a sync table configuration"""
    
    url = f"{BASE_URL}/sync-tables/{sync_table_id}"
    
    print(f"Deleting sync table ID {sync_table_id}...")
    
    try:
        response = requests.delete(url)
        
        if response.status_code == 200:
            print("Successfully deleted sync table configuration!")
            return True
        else:
            print(f"Error deleting sync table. Status code: {response.status_code}")
            print("Response:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False
    
if __name__ == "__main__":
    delete_sync_table(0)