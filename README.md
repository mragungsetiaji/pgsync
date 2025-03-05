# PGSync - PostgreSQL Data Extraction Tool

A lightweight API service for PostgreSQL database exploration and data extraction with support for incremental sync patterns.

## Features

- PostgreSQL database connection management
- Database schema exploration (tables, columns)
- Custom SQL query execution
- Incremental data extraction with cursor-based pagination
- Background job processing for large datasets
- Output as JSON files with timestamps
- Google Cloud integration:
  - Automatic upload to Google Cloud Storage (GCS)
  - Loading data from GCS to BigQuery
  - Schema translation from PostgreSQL to BigQuery
  - Configurable partitioning and clustering in BigQuery tables

## How to run
You can run the application in different modes:
1. API server: `uv run main.py --mode server`
2. Scheduler: `uv run main.py --mode scheduler --check-interval 60`
3. Celery worker: `uv run main.py --mode worker --loglevel=info --concurrency=4`

If you don't specify the mode, it defaults to running the server.
