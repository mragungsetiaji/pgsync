from typing import Dict, Any, List, Optional
from _config import BASE_URL
import requests

def create_sync_table(
    source_db_id: int, 
    table_name: str,
    cursor_column: str,
    batch_size: int = 1000,
    sync_interval: int = 60,
    is_active: bool = True
) -> Dict[str, Any]:
    """Create a new sync table configuration"""
    
    url = f"{BASE_URL}/sync-tables/"
    
    data = {
        "source_db_id": source_db_id,
        "table_name": table_name,
        "cursor_column": cursor_column,
        "batch_size": batch_size,
        "sync_interval": sync_interval,
        "is_active": is_active
    }
    
    print(f"Creating sync table for '{table_name}'...")
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("Successfully created sync table configuration!")
            return response.json()
        else:
            print(f"Error creating sync table. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
if __name__ == "__main__":
    result = create_sync_table(1, "account", "updated_at")
    if result:
        print("\nSync table configuration:")
        print(result)