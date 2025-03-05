import argparse
from datetime import datetime

def main():

    parser = argparse.ArgumentParser(description="Test the connection settings API")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    

    cron_parser = subparsers.add_parser("test-cron", help="Test a cron expression")
    cron_parser.add_argument("--cron", type=str, required=True, help="Cron expression to test")
    cron_parser.add_argument("--timezone", type=str, default="UTC", help="Timezone to use")
    
    args = parser.parse_args()

    if args.command == "test-cron":
        try:
            from croniter import croniter
            import pytz
            
            # Get the current time in the specified timezone
            tz = pytz.timezone(args.timezone)
            now = datetime.now(tz)
            
            # Parse the cron expression and get the next 5 occurrences
            cron = croniter(args.cron, now)
            
            print(f"Testing cron expression: {args.cron} in timezone {args.timezone}")
            print("\nNext 5 scheduled runs:")
            
            for i in range(5):
                next_time = cron.get_next(datetime)
                print(f"{i+1}. {next_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                
        except Exception as e:
            print(f"Error testing cron expression: {str(e)}")

if __name__ == "__main__":
    main()