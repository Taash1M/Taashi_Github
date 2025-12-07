# AWS Platform Modernization Implementation

## Overview

This folder contains a concrete Medallion-style data platform on AWS:

- **Bronze**: Raw CSV events in S3
- **Silver**: Cleaned, standardized Parquet in S3
- **Gold**: Hourly device metrics in S3, queried via Athena

Core tools:

- Amazon S3
- AWS Lambda
- AWS Glue
- Amazon Athena

---

## Sample Data

The canonical manufacturing IoT sample data lives at:

- `aws_implementation/sample_data/manufacturing_events.csv`

Typical columns:

- `timestamp`, `device_id`, `facility_id`, `temperature`, `pressure`,
  `vibration`, `status`, `production_rate`, `quality_score`

---

## End-to-End Flow

### 1. Lambda Ingestion (to Bronze)

File: `lambda_functions/ingest_events.py`

- Accepts JSON events (from Kinesis, API Gateway, or direct calls)
- Converts them to CSV
- Writes to:

```text
s3://data-platform-<ACCOUNT_ID>-bronze/manufacturing_events/bronze/YYYY/MM/DD/HH/events_YYYYMMDDHHMMSS.csv
```

### 2. Glue ETL (Bronze -> Silver)

File: `glue_jobs/bronze_to_silver.py`

- Reads CSV from Bronze S3
- Cleanses and standardizes data
- Writes partitioned Parquet to Silver S3

### 3. Athena SQL (Silver -> Gold)

File: `athena_sql/create_gold_tables.sql`

- Creates external table over Silver Parquet
- Materializes Gold table with hourly device metrics

---

## Running the Script

Execute this script to generate all artifacts:

```bash
python update_aws_implementation.py
```

This will create all necessary directories and files in the `aws_implementation` folder.

---

*Last updated: 2025-12-07*
