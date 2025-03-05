from typing import Dict, Any, List, Optional
from _config import BASE_URL
import requests

def list_sync_tables(
    source_db_id: Optional[int] = None,
    active_only: bool = False
) -> List[Dict[str, Any]]:
    """List all sync table configurations"""
    
    url = f"{BASE_URL}/sync-tables/"
    params = {}
    
    if source_db_id is not None:
        params["source_db_id"] = source_db_id
        
    if active_only:
        params["active_only"] = "true"
    
    print("Listing sync table configurations...")
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error listing sync tables. Status code: {response.status_code}")
            print("Response:", response.text)
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []
    
if __name__ == "__main__":
    sync_tables = list_sync_tables(
            source_db_id=1,
            active_only=True
        )
    print(f"\nFound {len(sync_tables)} sync table configurations:")
    for i, table in enumerate(sync_tables, 1):
        print(f"\n{i}. {table['table_name']} (ID: {table['id']})")
        print(f"   Source DB: {table['source_db_name']} (ID: {table['source_db_id']})")
        print(f"   Active: {'Yes' if table['is_active'] else 'No'}")
        print(f"   Interval: {table['sync_interval']} minutes")