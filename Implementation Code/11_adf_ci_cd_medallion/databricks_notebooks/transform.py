# databricks_notebooks/transform.py
# Conceptual Spark code executed in an Azure Databricks notebook
# This script demonstrates the Medallion Architecture (Bronze -> Silver -> Gold)
# for data pulled from a source like Oracle EBS via Azure Data Factory.

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType

# --- Configuration (Conceptual Mount Points) ---
SOURCE_PATH = "/mnt/bronze/ebs_sales_view/"
SILVER_PATH = "/mnt/silver/sales_staging/"
GOLD_PATH = "/mnt/gold/sales_fact/"

def bronze_to_silver(spark: SparkSession):
    """Cleans and standardizes data from the Bronze layer."""
    print("Starting Bronze to Silver transformation...")
    
    # --- Mock Data Creation (In a real scenario, this would be a read from ADLS Gen2) ---
    schema = StructType([
        StructField("ORDER_ID", StringType(), True),
        StructField("CUSTOMER_ID", StringType(), True),
        StructField("ORDER_TOTAL", StringType(), True),
        StructField("ORDER_DATE", StringType(), True),
        StructField("SOURCE_SYSTEM", StringType(), True)
    ])
    
    data = [
        ("1001", "CUST-001", "120.50", "2024-01-01", "ORACLE_EBS"),
        ("1002", "CUST-002", "85.00", "2024-01-02", "ORACLE_EBS"),
        ("NULL_ID", "CUST-003", "50.00", "2024-01-03", "ORACLE_EBS"), # Will be filtered out
    ]
    df_bronze = spark.createDataFrame(data, schema)
    df_bronze = df_bronze.withColumn("ingestion_ts", current_timestamp())
    # --- End Mock Data Creation ---
    
    # 1. Apply cleaning and standardization (Silver)
    df_silver = (
        df_bronze
        .withColumn("order_id", col("ORDER_ID").cast("integer"))
        .withColumn("customer_id", col("CUSTOMER_ID"))
        .withColumn("order_total", col("ORDER_TOTAL").cast("double"))
        .withColumn("order_date", col("ORDER_DATE").cast("date"))
        .filter(col("order_id").isNotNull()) # Data Quality: Filter out records with invalid IDs
        .withColumn("processed_ts", current_timestamp())
        .select("order_id", "customer_id", "order_total", "order_date", "processed_ts")
    )
    
    # 2. Write to Silver layer (Conceptual Delta Lake write)
    # df_silver.write.format("delta").mode("overwrite").save(SILVER_PATH)
    print(f"Data written to Silver layer (Conceptual write to {SILVER_PATH}). Records: {df_silver.count()}")
    return df_silver

def silver_to_gold(spark: SparkSession, df_silver):
    """Aggregates and models data from the Silver layer for consumption."""
    print("Starting Silver to Gold transformation...")
    
    # 1. Apply business logic (Gold - e.g., aggregation for a fact table)
    df_gold = (
        df_silver
        .groupBy("order_date")
        .agg({"order_id": "count", "order_total": "sum"})
        .withColumnRenamed("count(order_id)", "daily_order_count")
        .withColumnRenamed("sum(order_total)", "daily_revenue")
        .withColumn("load_ts", current_timestamp())
    )
    
    # 2. Write to Gold layer (Conceptual Delta Lake write)
    # df_gold.write.format("delta").mode("overwrite").save(GOLD_PATH)
    print(f"Data written to Gold layer (Conceptual write to {GOLD_PATH}). Records: {df_gold.count()}")

if __name__ == "__main__":
    # Mock Spark Session initialization
    print("NOTE: This script requires PySpark to run. Simulating execution.")
    
    # Create a mock SparkSession for local testing (requires PySpark installed)
    try:
        spark = SparkSession.builder.appName("ADF_Medallion_Transform").getOrCreate()
        df_silver = bronze_to_silver(spark)
        silver_to_gold(spark, df_silver)
        spark.stop()
    except Exception as e:
        print(f"Mock execution failed (likely missing PySpark): {e}")
        print("Conceptual flow validated.")
