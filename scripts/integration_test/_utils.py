from typing import Any, Dict

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