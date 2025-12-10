
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
    
    df_silver_orders = df_bronze_orders.withColumn("timestamp", to_timestamp(col("timestamp"))) \
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
