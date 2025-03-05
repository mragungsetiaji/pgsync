from typing import Dict, Any, Optional
from _config import BASE_URL
from _utils import print_sync_table
import requests

def update_sync_table(
    sync_table_id: int,
    is_active: Optional[bool] = None,
    cursor_column: Optional[str] = None,
    batch_size: Optional[int] = None,
    sync_interval: Optional[int] = None
) -> Dict[str, Any]:
    """Update a sync table configuration"""
    
    url = f"{BASE_URL}/sync-tables/{sync_table_id}"
    
    data = {}
    if is_active is not None:
        data["is_active"] = is_active
    if cursor_column is not None:
        data["cursor_column"] = cursor_column
    if batch_size is not None:
        data["batch_size"] = batch_size
    if sync_interval is not None:
        data["sync_interval"] = sync_interval
    
    print(f"Updating sync table ID {sync_table_id}...")
    
    try:
        response = requests.put(url, json=data)
        
        if response.status_code == 200:
            print("Successfully updated sync table configuration!")
            return response.json()
        else:
            print(f"Error updating sync table. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    active = False
        
    sync_table = update_sync_table(
        sync_table_id=1,
        is_active=active,
        cursor_column="updated_at",
        batch_size=1000,
        sync_interval=30
    )
    if sync_table:
        print_sync_table(sync_table)