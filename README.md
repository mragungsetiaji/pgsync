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