import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp

def get_spark():
    return (
        SparkSession.builder
        .appName("platform_modernization_ingest_sales")
        .getOrCreate()
    )

def main():
    spark = get_spark()

    raw_path = os.getenv("RAW_PATH", "data/raw/sales.csv")
    bronze_path = os.getenv("BRONZE_PATH", "data/bronze/sales")

    df = (
        spark.read
        .option("header", True)
        .csv(raw_path)
    )

    df = df.withColumn("ingestion_ts", current_timestamp())

    (
        df.write
        .mode("overwrite")
        .format("delta")
        .save(bronze_path)
    )

    print(f"Ingested raw sales data from {raw_path} to {bronze_path}")

if __name__ == "__main__":
    main()
