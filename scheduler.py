import sys
import time
import pytz

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from models.database import ConnectionSettings, ScheduleType, SyncTable, SourceDatabase
from datetime import datetime
from croniter import croniter
from pipeline.extract import add_extract_job
from utils import logger

# Create a database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Main scheduler loop
def run_scheduler(args):
    logger.info(f"Starting scheduler service with {args.check_interval} second interval...")
    try:
        while True:
            db = SessionLocal()
            try:
                logger.info("Checking for scheduled tasks...")
                # Get active connection settings
                active_settings = db.query(ConnectionSettings)\
                    .filter(ConnectionSettings.is_active == True)\
                    .all()
                
                current_time = datetime.now()
                for settings in active_settings:
                    # Skip manual connections
                    if settings.schedule_type == ScheduleType.MANUAL:
                        continue

                    # Check if it's time to run this connection
                    if settings.next_run_at and settings.next_run_at <= current_time:
                        logger.info(f"Running scheduled sync for connection: {settings.name} (ID: {settings.id})")
                        
                        # Get all active sync tables
                        sync_tables = db.query(SyncTable)\
                            .filter(SyncTable.is_active == True)\
                            .all()
                        
                        if not sync_tables:
                            logger.info(f"No active sync tables found for connection {settings.name}")
                            continue
                        
                        # Group sync tables by source db
                        tables_by_source = {}
                        for table in sync_tables:
                            if table.source_db_id not in tables_by_source:
                                tables_by_source[table.source_db_id] = []
                            tables_by_source[table.source_db_id].append(table)
                                
                            # Process each source database
                            for source_db_id, tables in tables_by_source.items():
                                # Get source db connection info
                                source_db = db.query(SourceDatabase)\
                                    .filter(SourceDatabase.id == source_db_id)\
                                    .first()
                                
                                if not source_db:
                                    logger.error(f"Source database with ID {source_db_id} not found")
                                    continue
                                
                                # Create connection parameters
                                conn_params = {
                                    "host": source_db.host,
                                    "port": source_db.port,
                                    "dbname": source_db.database,
                                    "user": source_db.user,
                                    "password": source_db.password
                                }

                                # Queue extract job for each table
                                for table in tables:
                                    try:
                                        # Add extraction job
                                        add_extract_job(
                                            source_db_id=source_db_id,
                                            table_name=table.table_name,
                                            cursor_column=table.cursor_column,
                                            cursor_value=None,  # Start from beginning
                                            batch_size=table.batch_size,
                                            conn_params=conn_params
                                        )
                                        
                                        logger.info(f"Queued extraction job for table: {table.table_name}")
                                    except Exception as e:
                                        logger.error(f"Failed to queue extraction for table {table.table_name}: {str(e)}")
                                
                            # Update next run time
                            if settings.cron_expression:
                                try:
                                    tz = pytz.timezone(settings.timezone or "UTC")
                                    now = datetime.now(tz)
                                    cron = croniter(settings.cron_expression, now)
                                    settings.next_run_at = cron.get_next(datetime)
                                    settings.last_run_at = current_time
                                    db.commit()
                                    logger.info(f"Updated next run time for {settings.name} to {settings.next_run_at}")
                                except Exception as e:
                                    logger.error(f"Failed to calculate next run time: {str(e)}")
            
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
            finally:
                db.close()
            
            # Wait for the next check interval
            logger.info(f"Sleeping for {args.check_interval} seconds...")
            time.sleep(args.check_interval)
                    
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        sys.exit(0)