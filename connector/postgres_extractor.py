import os
import json
import psycopg
import logging
from datetime import datetime
from core.base import BaseExtractor
from core.jobs import ExtractJob
from connector.postgres_source import PostgresSource
from worker.job_manager import update_job_status

logger = logging.getLogger("extract")

class PostgresExtractor(BaseExtractor):
    def __init__(self, conn_params, save_to_disk=True):
        super().__init__(conn_params)
        self.source = PostgresSource(**conn_params)
        self.output_dir = os.path.join(os.getcwd(), "data", "output")
        self.save_to_disk = save_to_disk
        if self.save_to_disk:
            os.makedirs(self.output_dir, exist_ok=True)

    def _validate_connection_params(self):
        self.source.check_connection()

    async def extract_incremental(self, job_dict):
        job = ExtractJob(**job_dict)
        extracted_batches = []  # Store batches if not saving to disk

        try:
            job.status = "running"
            job.updated_at = datetime.now().isoformat()
            cursor_value = job.cursor_value if job.cursor_value else "(0,0)" if job.use_ctid else None
            has_more_data = True
            batch_num = 0

            while has_more_data:
                batch_data, next_cursor_value = await self._extract_batch(
                    job.table_name, 
                    job.use_ctid, 
                    job.cursor_column if not job.use_ctid else None, 
                    cursor_value, 
                    job.batch_size
                )
                if len(batch_data) < job.batch_size or next_cursor_value == cursor_value:
                    has_more_data = False

                if batch_data:
                    batch_num += 1

                    # Save data to disk if configured
                    if self.save_to_disk:
                        file_path = self._get_output_path(job.table_name, job.id, batch_num)
                        self._save_to_json(batch_data, file_path)

                    # Always keep data in memory for return
                    extracted_batches.append(batch_data)

                    job.extracted_records += len(batch_data)
                    job.updated_at = datetime.now().isoformat()
                    job.cursor_value = next_cursor_value
                    cursor_value = next_cursor_value
                    update_job_status(job)
                else:
                    has_more_data = False

            job.status = "completed"
            job.updated_at = datetime.now().isoformat()
            update_job_status(job)

            # Return both status and extracted data
            return {
                "success": True,
                "job_id": job.id,
                "table_name": job.table_name,
                "records_extracted": job.extracted_records,
                "batches": extracted_batches
            }
        
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            job.status = "failed"
            job.error = str(e)
            job.updated_at = datetime.now().isoformat()
            update_job_status(job)
            return {
                "success": False,
                "error": str(e),
                "job_id": job.id
            }

    async def _extract_batch(self, table_name, use_ctid, cursor_column, cursor_value, batch_size):
        if use_ctid:
            where_clause = "WHERE ctid > %s" if cursor_value else ""
            params = [cursor_value, batch_size] if cursor_value else [batch_size]
            query = f"SELECT *, ctid FROM {table_name} {where_clause} ORDER BY ctid ASC LIMIT %s"
        else:
            if not cursor_column:
                raise ValueError("Cursor column must be provided when not using CTID")
            where_clause = f"WHERE {cursor_column} > %s" if cursor_value else ""
            params = [cursor_value, batch_size] if cursor_value else [batch_size]
            query = f"SELECT * FROM {table_name} {where_clause} ORDER BY {cursor_column} ASC LIMIT %s"
        async with await psycopg.AsyncConnection.connect(**self.conn_params) as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                batch_data = []
                rows = await cur.fetchall()
                for row in rows:
                    row_dict = {columns[i]: value for i, value in enumerate(row)}
                    if use_ctid:
                        del row_dict["ctid"]
                    batch_data.append(row_dict)
                next_cursor_value = (rows[-1][columns.index("ctid")] if use_ctid else rows[-1][columns.index(cursor_column)]) if rows else cursor_value
                return batch_data, next_cursor_value

    def _get_output_path(self, table_name, job_id, batch_num):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{table_name}_{job_id}_{batch_num}_{timestamp}.json"
        return os.path.join(self.output_dir, filename)

    def _save_to_json(self, data, file_path):
        with open(file_path, "w") as f:
            json.dump(data, f)
        logger.info(f"Saved {len(data)} records to {file_path}")