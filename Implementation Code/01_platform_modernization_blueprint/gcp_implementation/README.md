# GCP Platform Modernization Implementation

## Overview

This folder contains a concrete Medallion-style data platform on **Google Cloud**:

- **Bronze**: Raw JSON in Cloud Storage (from CSV via Dataflow)
- **Silver**: Cleaned, standardized data in BigQuery (or Parquet in GCS)
- **Gold**: Hourly device metrics in BigQuery with user-friendly metrics

Core tools:

- Cloud Storage (GCS)
- Dataflow (Apache Beam)
- BigQuery

---

## Sample Data

The canonical manufacturing IoT sample data lives at:

- `gcp_implementation/sample_data/manufacturing_events.csv`

Typical columns:

- `timestamp`, `device_id`, `facility_id`, `temperature`, `pressure`,
  `vibration`, `status`, `production_rate`, `quality_score`

---

## End-to-End Flow

### 1. Dataflow Ingestion: CSV -> Bronze (JSON in GCS)

File: `dataflow_pipelines/ingest_to_bronze.py`

- Reads CSV from a GCS location
- Normalizes rows into JSON objects
- Writes line-delimited JSON files into:

```text
gs://<YOUR_BUCKET>/manufacturing_events/bronze/events-*.json
```

### 2. Dataflow ETL: Bronze -> Silver

File: `dataflow_pipelines/bronze_to_silver.py`

- Reads JSON from Bronze GCS
- Cleanses and standardizes data
- Writes to BigQuery Silver table (or Parquet in GCS)

### 3. BigQuery SQL: Silver -> Gold

File: `bigquery_sql/create_silver_and_gold_tables.sql`

- Creates Gold table with hourly device metrics
- Aggregates data with user-friendly column names

---

## Running the Script

Execute this script to generate all artifacts:

```bash
python update_gcp_implementation.py
```

This will create all necessary directories and files in the `gcp_implementation` folder.

---

*Last updated: 2025-12-07*
