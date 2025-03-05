import requests
import argparse
from _config import BASE_URL

def toggle_connection_setting(setting_id: int):
    """Toggle a connection setting's active status"""
    url = f"{BASE_URL}/connection-settings/{setting_id}/toggle"
    
    print(f"Toggling connection setting ID {setting_id}...")
    
    try:
        response = requests.post(url)
        
        if response.status_code == 200:
            result = response.json()
            print(result["message"])
            return result
        else:
            print(f"Error toggling connection setting. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def main():
    parser = argparse.ArgumentParser(description="Test the connection settings API")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    toggle_parser = subparsers.add_parser("toggle", help="Toggle a connection setting's active status")
    toggle_parser.add_argument("id", type=int, help="Connection setting ID")

    args = parser.parse_args()
    if args.command == "toggle":
        toggle_connection_setting(args.id)

if __name__ == "__main__":
    main()