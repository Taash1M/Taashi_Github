from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count

def main():
    spark = (
        SparkSession.builder
        .appName("netflix_scale_pipeline")
        .getOrCreate()
    )

    # For local demo, treat file as streaming source
    df = (
        spark.readStream
        .format("json")
        .schema("user_id INT, event_type STRING, timestamp LONG, device STRING")
        .load("events_dir")
    )

    agg = (
        df.withColumn("ts", (col("timestamp").cast("timestamp")))
        .groupBy(
            window(col("ts"), "5 minutes"),
            col("event_type")
        )
        .agg(count("*").alias("event_count"))
    )

    query = (
        agg.writeStream
        .format("console")
        .outputMode("update")
        .start()
    )

    query.awaitTermination()

if __name__ == "__main__":
    main()
