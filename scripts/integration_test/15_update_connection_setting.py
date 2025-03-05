import requests
import json
import argparse
from _config import BASE_URL
from _utils import print_connection_setting

def update_connection_setting(
    setting_id: int,
    name: str = None,
    schedule_type: str = None,
    cron_expression: str = None,
    timezone: str = None,
    is_active: bool = None,
    connection_state: dict = None
):
    """Update a connection setting"""
    url = f"{BASE_URL}/connection-settings/{setting_id}"
    
    data = {}
    if name is not None:
        data["name"] = name
    if schedule_type is not None:
        data["schedule_type"] = schedule_type
    if cron_expression is not None:
        data["cron_expression"] = cron_expression
    if timezone is not None:
        data["timezone"] = timezone
    if is_active is not None:
        data["is_active"] = is_active
    if connection_state is not None:
        data["connection_state"] = connection_state
    
    print(f"Updating connection setting ID {setting_id}...")
    
    try:
        response = requests.put(url, json=data)
        
        if response.status_code == 200:
            print("Successfully updated connection setting!")
            return response.json()
        else:
            print(f"Error updating connection setting. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def main():
    parser = argparse.ArgumentParser(description="Test the connection settings API")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    update_parser = subparsers.add_parser("update", help="Update a connection setting")
    update_parser.add_argument("id", type=int, help="Connection setting ID")
    update_parser.add_argument("--name", type=str, help="New name")
    update_parser.add_argument("--type", type=str, choices=["manual", "cron"], help="New schedule type")
    update_parser.add_argument("--cron", type=str, help="New cron expression")
    update_parser.add_argument("--timezone", type=str, help="New timezone")
    update_parser.add_argument("--active", action="store_true", help="Set active")
    update_parser.add_argument("--inactive", action="store_true", help="Set inactive")
    update_parser.add_argument("--state", type=str, help="New JSON string for connection state")

    args = parser.parse_args()
    if args.command == "update":
        # Determine active status based on arguments
        active = None
        if args.active and not args.inactive:
            active = True
        elif args.inactive and not args.active:
            active = False
        
        # Parse connection state if provided
        conn_state = None
        if args.state:
            try:
                conn_state = json.loads(args.state)
            except json.JSONDecodeError:
                print("Error: Invalid JSON for connection state")
                return
        
        setting = update_connection_setting(
            setting_id=args.id,
            name=args.name,
            schedule_type=args.type,
            cron_expression=args.cron,
            timezone=args.timezone,
            is_active=active,
            connection_state=conn_state
        )
        
        if setting:
            print_connection_setting(setting)

if __name__ == "__main__":
    main()