from typing import Any, Dict
import datetime

def print_sync_table(sync_table: Dict[str, Any]) -> None:
    """Pretty print a sync table configuration"""
    print("\nSync Table Configuration:")
    print(f"ID:              {sync_table['id']}")
    print(f"Table:           {sync_table['table_name']}")
    print(f"Source DB:       {sync_table['source_db_name']} (ID: {sync_table['source_db_id']})")
    print(f"Active:          {'Yes' if sync_table['is_active'] else 'No'}")
    print(f"Cursor Column:   {sync_table['cursor_column']}")
    print(f"Batch Size:      {sync_table['batch_size']}")
    print(f"Sync Interval:   {sync_table['sync_interval']} minutes")
    print(f"Last Synced:     {sync_table['last_synced_at'] or 'Never'}")
    print(f"Created:         {sync_table['created_at']}")
    print(f"Updated:         {sync_table['updated_at']}")

def print_connection_setting(setting):
    """Pretty print a connection setting"""
    print("\nConnection Setting Details:")
    print(f"ID:             {setting['id']}")
    print(f"Name:           {setting['name']}")
    print(f"Schedule Type:  {setting['schedule_type']}")
    
    if setting['schedule_type'] == 'cron':
        print(f"Cron:           {setting['cron_expression']}")
        print(f"Timezone:        {setting['timezone']}")
        
        # Show next/last run times in a readable format
        if setting['next_run_at']:
            next_run = datetime.fromisoformat(setting['next_run_at'].replace('Z', '+00:00'))
            print(f"Next Run:       {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
        if setting['last_run_at']:
            last_run = datetime.fromisoformat(setting['last_run_at'].replace('Z', '+00:00'))
            print(f"Last Run:       {last_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    print(f"Active:         {'Yes' if setting['is_active'] else 'No'}")
    
    if setting['connection_state']:
        print("Connection State:")
        for key, value in setting['connection_state'].items():
            print(f"  {key}: {value}")
    
    print(f"Created:        {setting['created_at']}")
    print(f"Updated:        {setting['updated_at']}")