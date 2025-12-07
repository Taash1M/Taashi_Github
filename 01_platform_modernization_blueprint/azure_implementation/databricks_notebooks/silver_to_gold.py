# Databricks notebook source
# Silver -> Gold transformation for manufacturing events

from pyspark.sql import functions as F
from pyspark.sql import SparkSession

silver_path = dbutils.widgets.get("silver_path") if "silver_path" in dbutils.widgets.getArgumentNames() else "abfss://silver@<STORAGE_ACCOUNT>.dfs.core.windows.net/manufacturing_events/silver"
gold_path = dbutils.widgets.get("gold_path") if "gold_path" in dbutils.widgets.getArgumentNames() else "abfss://gold@<STORAGE_ACCOUNT>.dfs.core.windows.net/manufacturing_events/gold"

spark = SparkSession.builder.getOrCreate()

print(f"Reading Silver data from: {silver_path}")
df_silver = spark.read.format("delta").load(silver_path)
print(f"Silver records: {df_silver.count()}")

# Example: aggregate to hourly metrics per device and facility
df_gold = (
    df_silver
    .withColumn("event_hour", F.date_trunc("HOUR", F.col("timestamp")))
    .groupBy("event_hour", "device_id", "facility_id")
    .agg(
        F.count("*").alias("events_count"),
        F.avg("temperature_c").alias("avg_temperature_c"),
        F.avg("pressure_kpa").alias("avg_pressure_kpa"),
        F.avg("vibration_mm_s").alias("avg_vibration_mm_s"),
        F.avg("production_rate").alias("avg_units_per_hour"),
        F.avg("quality_score").alias("avg_quality_score"),
        F.sum(F.when(F.col("status") == "WARNING", 1).otherwise(0)).alias("warning_events"),
        F.sum(F.when(F.col("status") == "CRITICAL", 1).otherwise(0)).alias("critical_events"),
    )
    .withColumnRenamed("event_hour", "hour_start")
    .withColumn("is_high_quality", F.col("avg_quality_score") >= 95.0)
    .withColumn("is_high_risk", F.col("critical_events") > 0)
)

print(f"Gold records: {df_gold.count()}")

(
    df_gold.write
    .format("delta")
    .mode("overwrite")
    .save(gold_path)
)

print(f"✓ Gold data written to: {gold_path}")
