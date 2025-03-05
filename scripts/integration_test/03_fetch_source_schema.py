import requests
from _config import BASE_URL

def fetch_schema(source_id, refresh=False):
    """
    Fetch schema for a source database
    
    Args:
        source_id: ID of the source database
        refresh: Whether to force a refresh of the schema
    """
    url = f"{BASE_URL}/sources/{source_id}/schema"
    if refresh:
        url += "?refresh=true"
    
    try:
        print(f"Fetching schema for source ID {source_id}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            print("Successfully fetched schema!")
            return response.json()
        else:
            print(f"Error fetching schema. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    

if __name__ == "__main__":
    result = fetch_schema(1, refresh=False)
    if result:
        # Print table count and first few tables for readability
        tables = result.get("tables", {})
        print(f"\nFound {len(tables)} tables in schema.")
        if tables:
            print("\nSample tables:")
            for i, (table_name, table_info) in enumerate(tables.items()):
                if i >= 3:  # Show only first 3 tables
                    print("...")
                    break
                print(f"- {table_name}: {len(table_info.get('columns', []))} columns")