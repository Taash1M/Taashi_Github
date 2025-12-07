# Databricks notebook source
# Bronze -> Silver transformation for manufacturing events

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql import SparkSession

# Use dbutils.widgets in Databricks to parameterize paths
# In ADF, these map to baseParameters.
bronze_path = dbutils.widgets.get("bronze_path") if "bronze_path" in dbutils.widgets.getArgumentNames() else "abfss://bronze@<STORAGE_ACCOUNT>.dfs.core.windows.net/manufacturing_events/bronze"
silver_path = dbutils.widgets.get("silver_path") if "silver_path" in dbutils.widgets.getArgumentNames() else "abfss://silver@<STORAGE_ACCOUNT>.dfs.core.windows.net/manufacturing_events/silver"

spark = SparkSession.builder.getOrCreate()

print(f"Reading Bronze data from: {bronze_path}")
df_bronze = spark.read.parquet(bronze_path)
print(f"Bronze records: {df_bronze.count()}")

# Basic cleansing and standardization
df_silver = (
    df_bronze
    .withColumn("timestamp", F.to_timestamp("timestamp", "yyyy-MM-dd HH:mm:ss"))
    .filter(F.col("timestamp").isNotNull())
    .filter(F.col("device_id").isNotNull())
    .withColumn("device_id", F.upper(F.trim("device_id")))
    .withColumn("facility_id", F.upper(F.trim("facility_id")))
    .withColumn(
        "temperature_c",
        F.col("temperature").cast("double"),
    )
    .withColumn(
        "pressure_kpa",
        F.col("pressure").cast("double"),
    )
    .withColumn(
        "vibration_mm_s",
        F.col("vibration").cast("double"),
    )
    .withColumn("production_rate", F.col("production_rate").cast("int"))
    .withColumn("quality_score", F.col("quality_score").cast("double"))
    .withColumn("processed_timestamp", F.current_timestamp())
    .withColumn("process_date", F.to_date("timestamp"))
    .dropDuplicates(["timestamp", "device_id"])
)

print(f"Silver records after cleansing: {df_silver.count()}")

(
    df_silver.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("process_date", "facility_id")
    .save(silver_path)
)

print(f"✓ Silver data written to: {silver_path}")
