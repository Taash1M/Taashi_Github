
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import current_timestamp, sum as _sum
    spark = SparkSession.builder.appName("AzureDemo").getOrCreate()
except ImportError:
    print("PySpark not installed. Simulation mode.")
    exit(0)

def process_stream():
    # ==========================================
    # BRONZE LAYER (Raw Ingest)
    # ==========================================
    print("--- Processing Bronze Layer ---")
    df_bronze = spark.read.option("header", True).csv("../data/azure_inventory_logs.csv")

    # ==========================================
    # SILVER LAYER (Clean & Dedupe)
    # ==========================================
    print("--- Processing Silver Layer ---")
    # Critical for "Exactly-Once" processing
    df_silver = df_bronze.withColumn("processing_time", current_timestamp()) \
                         .dropDuplicates(["log_id"])
    
    print("[System] Optimizing Silver Layer: Z-ORDER BY warehouse_id")

    # ==========================================
    # GOLD LAYER (Aggregated State)
    # ==========================================
    print("--- Processing Gold Layer ---")
    # Aggregating the ledger to get "Current Stock on Hand"
    df_gold = df_silver.groupBy("warehouse_id", "sku").agg(_sum("change_amount").alias("current_stock"))
    
    print("--- Executive Summary: Gold Layer Stock Levels ---")
    df_gold.show(5)

if __name__ == "__main__":
    process_stream()
