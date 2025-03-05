from _config import BASE_URL
import requests

def toggle_sync_table(sync_table_id: int) -> bool:
    """Toggle the active status of a sync table"""
    
    url = f"{BASE_URL}/sync-tables/{sync_table_id}/toggle"
    
    print(f"Toggling sync table ID {sync_table_id}...")
    
    try:
        response = requests.post(url)
        
        if response.status_code == 200:
            result = response.json()
            print(result["message"])
            return True
        else:
            print(f"Error toggling sync table. Status code: {response.status_code}")
            print("Response:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False
    
if __name__ == "__main__":
    toggle_sync_table(1)