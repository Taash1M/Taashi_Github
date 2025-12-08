import time
from pyspark.sql import SparkSession

def main():
    spark = (
        SparkSession.builder
        .appName("optimized_job")
        .config("spark.sql.shuffle.partitions", "200")
        .getOrCreate()
    )

    start = time.time()
    df = (
        spark.read
        .option("header", True)
        .csv("data/large_orders.csv")
        .repartition("customer_id")
    )

    agg = df.groupBy("customer_id").count()
    agg.cache()
    agg.collect()
    elapsed = time.time() - start
    print(f"Optimized job took {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
