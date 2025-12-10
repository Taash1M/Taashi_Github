import time
from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("naive_job").getOrCreate()

    start = time.time()
    df = spark.read.option("header", True).csv("data/large_orders.csv")
    agg = df.groupBy("customer_id").count()
    agg.collect()
    elapsed = time.time() - start
    print(f"Naive job took {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
