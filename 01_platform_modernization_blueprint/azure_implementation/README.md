# Azure Platform Modernization Implementation

## Overview

This folder contains a concrete, runnable example of a Medallion Architecture on Azure using **real sample data** and **real artifacts**:

- Source CSV: `aws_implementation/sample_data/manufacturing_events.csv` (copied locally into this folder)
- Azure Data Factory pipeline: `adf_pipelines/pl_csv_to_medallion.json`
- Azure Databricks notebooks:
  - `databricks_notebooks/bronze_to_silver.py`
  - `databricks_notebooks/silver_to_gold.py`
- Azure Synapse SQL script:
  - `synapse_scripts/create_gold_table.sql`

The design follows **Bronze → Silver → Gold**:

- **Bronze**: Raw Parquet landing
- **Silver**: Cleaned + standardized Delta Lake
- **Gold**: Hourly device metrics with friendly column names and business logic

---

## End-to-End Flow

1. **Sample Data Copy**

   The script `update_azure_modernization.py` copies the canonical sample data from:

   ```text
   01_platform_modernization_blueprint/aws_implementation/sample_data/manufacturing_events.csv
   ```

   into `azure_implementation/sample_data/manufacturing_events.csv`.

2. **ADF Pipeline Execution**

   The pipeline `pl_csv_to_medallion.json` orchestrates:
   - Copy CSV → Bronze (Parquet)
   - Trigger Databricks notebook: Bronze → Silver
   - Trigger Databricks notebook: Silver → Gold

3. **Databricks Notebooks**

   - `bronze_to_silver.py`: Cleanses and standardizes data
   - `silver_to_gold.py`: Aggregates to hourly device metrics

4. **Synapse SQL**

   The `create_gold_table.sql` script creates a final table for reporting.

---

## Running the Script

Execute this script to generate all artifacts:

```bash
python update_azure_implementation.py
```

This will create all necessary directories and files in the `azure_implementation` folder.

---

*Last updated: 2025-12-07*
