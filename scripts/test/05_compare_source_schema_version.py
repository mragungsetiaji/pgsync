import requests
from _config import BASE_URL

def compare_schema_versions(source_id, version1, version2):
    """Compare two schema versions"""
    url = f"{BASE_URL}/sources/{source_id}/schema/diff?version1={version1}&version2={version2}"
    
    try:
        print(f"Comparing schema versions {version1} and {version2} for source ID {source_id}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            print("Successfully compared schema versions!")
            return response.json()
        else:
            print(f"Error comparing schema versions. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
if __name__ == "__main__":

    diff = compare_schema_versions(1, 1, 2)
    if diff:
        print("\nSchema differences:")
        changes = diff.get("changes", {})
        
        added = changes.get("added_tables", [])
        if added:
            print(f"\nAdded tables ({len(added)}):")
            for table in added:
                print(f"+ {table}")
        
        removed = changes.get("removed_tables", [])
        if removed:
            print(f"\nRemoved tables ({len(removed)}):")
            for table in removed:
                print(f"- {table}")
        
        modified = changes.get("modified_tables", {})
        if modified:
            print(f"\nModified tables ({len(modified)}):")
            for table, mods in modified.items():
                print(f"~ {table}:")
                
                added_cols = mods.get("added_columns", [])
                if added_cols:
                    print("  Added columns:")
                    for col in added_cols:
                        print(f"  + {col}")
                
                removed_cols = mods.get("removed_columns", [])
                if removed_cols:
                    print("  Removed columns:")
                    for col in removed_cols:
                        print(f"  - {col}")
                
                changed_cols = mods.get("changed_columns", {})
                if changed_cols:
                    print("  Changed columns:")
                    for col, changes in changed_cols.items():
                        print(f"  ~ {col}: {changes.get('old_type')} -> {changes.get('new_type')}")
        
        if not added and not removed and not modified:
            print("No differences found between these schema versions.")