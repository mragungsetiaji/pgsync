import requests
import argparse
from _config import BASE_URL
from _utils import print_connection_setting

def get_connection_setting(setting_id: int):
    """Get a specific connection setting"""
    url = f"{BASE_URL}/connection-settings/{setting_id}"
    
    print(f"Getting connection setting with ID {setting_id}...")
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting connection setting. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def main():
    parser = argparse.ArgumentParser(description="Test the connection settings API")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    get_parser = subparsers.add_parser("get", help="Get a specific connection setting")
    get_parser.add_argument("id", type=int, help="Connection setting ID")

    args = parser.parse_args()
    if args.command == "get":
        setting = get_connection_setting(args.id)
        if setting:
            print_connection_setting(setting)

if __name__ == "__main__":
    main()