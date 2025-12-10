# 11. Azure Data Factory CI/CD with Medallion Architecture

## 💡 Project Overview: Enterprise Azure Integration

This project demonstrates a conceptual **Azure-native data pipeline** that integrates a legacy on-premise system (Oracle EBS) with a modern cloud data lake (Azure Data Lake Storage Gen2) and processing engine (Azure Databricks), all orchestrated via **Azure Data Factory (ADF)** and governed by a **Medallion Architecture**.

This showcases expertise in:
*   **Azure Data Services:** ADF, ADLS Gen2, Azure Databricks.
*   **Enterprise Integration:** Connecting to complex, on-premise sources (Oracle EBS).
*   **CI/CD for ADF:** Using GitHub Actions (or Azure DevOps) for automated deployment of ADF pipelines.
*   **Medallion Architecture:** Implementing Bronze (Raw), Silver (Staging), and Gold (Curated) layers for data quality and governance.

## 🏗️ Conceptual Architecture Flow

1.  **Source:** On-premise Oracle EBS Custom View (e.g., `EBS_SALES_VIEW`).
2.  **Ingestion (ADF):** ADF Copy Activity uses a Self-Hosted Integration Runtime (SHIR) to securely pull data.
3.  **Bronze Layer (ADLS Gen2):** Raw, immutable data landing zone (e.g., JSON/CSV).
4.  **Silver Layer (Databricks/Spark):** ADF triggers a Databricks notebook to clean, standardize, and apply initial quality checks.
5.  **Gold Layer (Databricks/Delta):** Final, aggregated, and business-ready data, optimized for consumption.

## 💻 Code Artifacts (Conceptual)

Since ADF pipelines are defined in JSON, this project provides conceptual JSON files and a CI/CD workflow to illustrate the process.

| File | Type | Purpose |
| :--- | :--- | :--- |
| `adf_pipelines/PL_EBS_TO_GOLD.json` | ADF Pipeline JSON | Main orchestration pipeline (Copy -> Databricks Notebook). |
| `adf_pipelines/DS_ORACLE_EBS.json` | ADF Dataset JSON | Defines the connection to the Oracle EBS source. |
| `databricks_notebooks/transform.py` | Python/Spark | Databricks notebook code for Silver/Gold transformations. |
| `.github/workflows/adf_ci_cd.yml` | GitHub Actions YAML | Conceptual CI/CD for deploying ADF changes via ARM templates. |

## ⚙️ Databricks Transformation (`transform.py`)

```python
# databricks_notebooks/transform.py
# Conceptual Spark code executed in an Azure Databricks notebook

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp

# Assume parameters are passed from ADF (e.g., source_path, target_path)
SOURCE_PATH = "/mnt/bronze/ebs_sales_view/"
SILVER_PATH = "/mnt/silver/sales_staging/"
GOLD_PATH = "/mnt/gold/sales_fact/"

def bronze_to_silver(spark: SparkSession):
    """Cleans and standardizes data from the Bronze layer."""
    print("Starting Bronze to Silver transformation...")
    
    # 1. Read raw data (Bronze)
    df_bronze = spark.read.format("delta").load(SOURCE_PATH)
    
    # 2. Apply cleaning and standardization (Silver)
    df_silver = (
        df_bronze
        .withColumn("order_id", col("ORDER_ID").cast("integer"))
        .withColumn("order_date", col("ORDER_DATE").cast("date"))
        .filter(col("order_id").isNotNull()) # Simple DQ check
        .withColumn("processed_ts", current_timestamp())
    )
    
    # 3. Write to Silver layer
    df_silver.write.format("delta").mode("overwrite").save(SILVER_PATH)
    print(f"Data written to Silver layer: {SILVER_PATH}")

def silver_to_gold(spark: SparkSession):
    """Aggregates and models data from the Silver layer for consumption."""
    print("Starting Silver to Gold transformation...")
    
    # 1. Read Silver data
    df_silver = spark.read.format("delta").load(SILVER_PATH)
    
    # 2. Apply business logic (Gold - e.g., aggregation)
    df_gold = (
        df_silver
        .groupBy("order_date")
        .agg({"order_id": "count", "order_total": "sum"})
        .withColumnRenamed("count(order_id)", "daily_order_count")
        .withColumnRenamed("sum(order_total)", "daily_revenue")
    )
    
    # 3. Write to Gold layer
    df_gold.write.format("delta").mode("overwrite").save(GOLD_PATH)
    print(f"Data written to Gold layer: {GOLD_PATH}")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("ADF_Medallion_Transform").getOrCreate()
    bronze_to_silver(spark)
    silver_to_gold(spark)
    spark.stop()
```
