import requests
import argparse
from _config import BASE_URL

def delete_connection_setting(setting_id: int):
    """Delete a connection setting"""
    url = f"{BASE_URL}/connection-settings/{setting_id}"
    
    print(f"Deleting connection setting ID {setting_id}...")
    
    try:
        response = requests.delete(url)
        
        if response.status_code == 200:
            print("Successfully deleted connection setting!")
            return response.json()
        else:
            print(f"Error deleting connection setting. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def main():
    parser = argparse.ArgumentParser(description="Test the connection settings API")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    delete_parser = subparsers.add_parser("delete", help="Delete a connection setting")
    delete_parser.add_argument("id", type=int, help="Connection setting ID")

    args = parser.parse_args()
    if args.command == "delete":
        delete_connection_setting(args.id)
    
if __name__ == "__main__":
    main()