import os
import random
import datetime

def setup_aws_environment():
    # 1. SETUP
    base_path = "/workspaces/Taashi_Github/Implementation Code/01_platform_modernization_blueprint"
    data_path = os.path.join(base_path, "data")
    aws_path = os.path.join(base_path, "aws_implementation")
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(aws_path, exist_ok=True)

    # 2. GENERATE DATA
    print("Generating AWS Data...")
    with open(os.path.join(data_path, "aws_ad_impressions.csv"), "w") as f:
        f.write("event_id,user_id,campaign_id,timestamp,platform,region\n")
        for i in range(1000):
            ts = datetime.datetime.now() - datetime.timedelta(seconds=random.randint(1, 10000))
            f.write(f"evt_{i},u_{random.randint(1,500)},cmp_{random.randint(1,5)},{ts},Meta_Ads,US-EAST\n")
    with open(os.path.join(data_path, "aws_orders.csv"), "w") as f:
        f.write("order_id,user_id,amount,timestamp,currency,sku\n")
        for i in range(200):
            ts = datetime.datetime.now() - datetime.timedelta(seconds=random.randint(1, 10000))
            f.write(f"ord_{i},u_{random.randint(1,500)},{random.randint(50,500)},{ts},USD,sku_{random.randint(100,105)}\n")

    # 3. INJECT CODE (Refactored for Medallion)
    glue_script = """
import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col, to_timestamp

def main():
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    
    # ==========================================
    # BRONZE LAYER (Raw Ingest)
    # ==========================================
    print("--- Processing Bronze Layer ---")
    df_bronze_ads = spark.read.option("header", True).csv("../data/aws_ad_impressions.csv")
    df_bronze_orders = spark.read.option("header", True).csv("../data/aws_orders.csv")
    
    # ==========================================
    # SILVER LAYER (Clean & Standardize)
    # ==========================================
    print("--- Processing Silver Layer ---")
    # Cast timestamps and enforce schema
    df_silver_ads = df_bronze_ads.withColumn("timestamp", to_timestamp(col("timestamp")))
    
    df_silver_orders = df_bronze_orders.withColumn("timestamp", to_timestamp(col("timestamp"))) \\
                                       .filter(col("sku").isNotNull()) # Quality Check
    
    # ==========================================
    # GOLD LAYER (Business Logic / Aggregation)
    # ==========================================
    print("--- Processing Gold Layer ---")
    # The "Hard" Join: Attributing Revenue to Campaigns
    df_joined = df_silver_ads.join(
        df_silver_orders,
        (df_silver_ads.user_id == df_silver_orders.user_id) & 
        (df_silver_orders.timestamp > df_silver_ads.timestamp),
        "inner"
    )
    
    df_gold_roas = df_joined.groupBy("campaign_id").sum("amount").withColumnRenamed("sum(amount)", "total_revenue")
    
    print("--- Executive Summary: Gold Layer ROAS ---")
    df_gold_roas.show()

if __name__ == "__main__":
    main()
"""
    with open(os.path.join(aws_path, "glue_etl_job.py"), "w") as f:
        f.write(glue_script)

    # 4. README UPDATE
    readme_content = """
# AWS Module: Global Omni-Channel Attribution Lakehouse

## 1. Executive Summary & Problem Statement
**The Challenge:** Marketing data is "messy" and high-velocity, while financial data is strict and transactional. Bridging this gap to calculate Real-Time ROAS (Return on Ad Spend) is difficult.
**The Solution:** A Serverless Attribution Lakehouse using AWS Glue.

## 2. Medallion Architecture Implementation
* **Bronze:** Raw ingestion of Ad Impressions and Orders from S3.
* **Silver:** Type enforcement (Timestamps) and Data Quality checks (Null SKU removal).
* **Gold:** Stateful temporal join to link specific Ad Impressions to Orders, aggregated by Campaign ID.

## 3. How to Run
1.  `cd aws_implementation`
2.  `python glue_etl_job.py`
"""
    with open(os.path.join(aws_path, "README.md"), "w") as f:
        f.write(readme_content)
    print("✅ AWS Environment Setup Complete (Medallion Enforced).")

if __name__ == "__main__":
    setup_aws_environment()