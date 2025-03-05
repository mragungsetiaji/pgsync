import requests
import json
import argparse
from _config import BASE_URL
from _utils import print_connection_setting

def create_connection_setting(
    name: str,
    schedule_type: str = "manual",
    cron_expression: str = None,
    timezone: str = "UTC",
    is_active: bool = True,
    connection_state: dict = None
):
    """Create a new connection setting"""
    url = f"{BASE_URL}/connection-settings/"
    
    data = {
        "name": name,
        "schedule_type": schedule_type,
        "is_active": is_active,
        "timezone": timezone
    }
    
    if cron_expression:
        data["cron_expression"] = cron_expression
        
    if connection_state:
        data["connection_state"] = connection_state
    
    print(f"Creating connection setting: {name}...")
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("Successfully created connection setting!")
            return response.json()
        else:
            print(f"Error creating connection setting. Status code: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Test the connection settings API")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    create_parser = subparsers.add_parser("create", help="Create a new connection setting")
    create_parser.add_argument("--name", type=str, required=True, help="Setting name")
    create_parser.add_argument("--type", type=str, choices=["manual", "cron"], default="manual", help="Schedule type")
    create_parser.add_argument("--cron", type=str, help="Cron expression (required for cron type)")
    create_parser.add_argument("--timezone", type=str, default="UTC", help="Timezone (for cron)")
    create_parser.add_argument("--inactive", action="store_true", help="Create as inactive")
    create_parser.add_argument("--state", type=str, help="JSON string for connection state")

    args = parser.parse_args()
    if args.command == "create":
        # Parse connection state if provided
        conn_state = None
        if args.state:
            try:
                conn_state = json.loads(args.state)
            except json.JSONDecodeError:
                print("Error: Invalid JSON for connection state")
                return
        
        # Check if cron expression is provided for cron type
        if args.type == "cron" and not args.cron:
            print("Error: Cron expression is required for cron schedule type")
            return
        
        result = create_connection_setting(
            name=args.name,
            schedule_type=args.type,
            cron_expression=args.cron,
            timezone=args.timezone,
            is_active=not args.inactive,
            connection_state=conn_state
        )
        
        if result:
            print_connection_setting(result)

if __name__ == "__main__":
    main()
