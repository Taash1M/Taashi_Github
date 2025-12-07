"""
Glue ETL job: Bronze -> Silver for manufacturing events.

Reads CSV from S3 Bronze prefix:
  s3://data-platform-<ACCOUNT_ID>-bronze/manufacturing_events/bronze/

Writes Parquet to S3 Silver prefix:
  s3://data-platform-<ACCOUNT_ID>-silver/manufacturing_events/silver/
"""

import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F


args = getResolvedOptions(sys.argv, ["JOB_NAME", "BRONZE_BUCKET", "SILVER_BUCKET"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

BRONZE_PATH = f"s3://{args['BRONZE_BUCKET']}/manufacturing_events/bronze/"
SILVER_PATH = f"s3://{args['SILVER_BUCKET']}/manufacturing_events/silver/"

print(f"Reading Bronze data from: {BRONZE_PATH}")

df_bronze = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(BRONZE_PATH)
)

print(f"Bronze record count: {df_bronze.count()}")

df_silver = (
    df_bronze
    .withColumn("timestamp", F.to_timestamp("timestamp", "yyyy-MM-dd HH:mm:ss"))
    .filter(F.col("timestamp").isNotNull())
    .filter(F.col("device_id").isNotNull())
    .withColumn("device_id", F.upper(F.trim("device_id")))
    .withColumn("facility_id", F.upper(F.trim("facility_id")))
    .withColumn("temperature_c", F.col("temperature").cast("double"))
    .withColumn("pressure_kpa", F.col("pressure").cast("double"))
    .withColumn("vibration_mm_s", F.col("vibration").cast("double"))
    .withColumn("production_rate", F.col("production_rate").cast("int"))
    .withColumn("quality_score", F.col("quality_score").cast("double"))
    .withColumn("process_date", F.to_date("timestamp"))
    .withColumn("processed_timestamp", F.current_timestamp())
    .dropDuplicates(["timestamp", "device_id"])
)

print(f"Silver record count: {df_silver.count()}")

(
    df_silver
    .write
    .mode("overwrite")
    .partitionBy("process_date", "facility_id")
    .parquet(SILVER_PATH)
)

print(f"✓ Wrote Silver data to: {SILVER_PATH}")

job.commit()
