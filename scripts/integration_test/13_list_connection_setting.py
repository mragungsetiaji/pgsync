import requests
import argparse
from _config import BASE_URL

def list_connection_settings(active_only: bool = False):
    """List all connection settings"""
    url = f"{BASE_URL}/connection-settings/"
    params = {}
    
    if active_only:
        params["active_only"] = "true"
    
    print("Listing connection settings...")
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error listing connection settings. Status code: {response.status_code}")
            print("Response:", response.text)
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Test the connection settings API")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    list_parser = subparsers.add_parser("list", help="List connection settings")
    list_parser.add_argument("--active-only", action="store_true", help="Show only active settings")

    args = parser.parse_args()
    if args.command == "list":
        settings = list_connection_settings(active_only=args.active_only)
        
        print(f"\nFound {len(settings)} connection settings:")
        for i, setting in enumerate(settings, 1):
            print(f"\n{i}. {setting['name']} (ID: {setting['id']})")
            print(f"   Type: {setting['schedule_type']}")
            if setting['schedule_type'] == 'cron':
                print(f"   Cron: {setting['cron_expression']}")
            print(f"   Active: {'Yes' if setting['is_active'] else 'No'}")

if __name__ == "__main__":
    main()