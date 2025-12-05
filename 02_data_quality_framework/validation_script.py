# validation_script.py
# This script demonstrates a conceptual integration of Great Expectations with Apache Spark
# to enforce data quality checks on a distributed data set.

import os
from great_expectations.core import ExpectationSuite, ExpectationConfiguration
from great_expectations.data_context import DataContext
from great_expectations.dataset import SparkDFDataset
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# --- Configuration ---
EXPECTATION_SUITE_NAME = "manufacturing_events_suite"
DATA_ASSET_PATH = "data_assets/sample_manufacturing_events.csv"

def run_data_validation(spark: SparkSession, suite_name: str, data_path: str):
    """
    Loads data and runs the Great Expectations validation suite.
    """
    print(f"Loading data from: {data_path}")
    
    # Define schema for better control
    schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("machine_id", StringType(), True),
        StructField("temperature_celsius", IntegerType(), True)
    ])
    
    # In a real scenario, this would read from S3/ADLS/GCS
    df = spark.read.csv(data_path, header=True, schema=schema)
    
    # Create a Great Expectations Spark Dataset
    ge_df = SparkDFDataset(df)
    
    # --- Define Expectations Programmatically (Mocking the GE Suite) ---
    suite = ExpectationSuite(
        expectation_suite_name=suite_name,
        expectations=[
            ExpectationConfiguration(
                expectation_type="expect_column_to_exist",
                kwargs={"column": "event_id"}
            ),
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={"column": "temperature_celsius", "min_value": 0, "max_value": 100}
            ),
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_not_be_null",
                kwargs={"column": "machine_id"}
            )
        ]
    )
    
    print(f"Running validation with suite: {suite_name}")
    results = ge_df.validate(suite, only_return_failures=False)
    
    if results["success"]:
        print("\n✅ Validation Successful! Data is clean and ready for Gold layer.")
    else:
        print("\n❌ Validation Failed! Data quality issues detected.")
        # In a production pipeline, this would trigger an alert and halt the pipeline.
        
    return results

if __name__ == "__main__":
    # Initialize Spark Session (Mock - requires PySpark to be installed, which we will assume for the portfolio)
    # For a local run, this would be: SparkSession.builder.appName("DataQualityFramework").getOrCreate()
    
    # Mock SparkSession and data creation for demonstration purposes
    print("NOTE: This script requires PySpark and Great Expectations to run.")
    print("Simulating data creation and validation run...")
    
    # Create the data_assets directory
    os.makedirs("data_assets", exist_ok=True)
    
    # Create a dummy data file for the script to read
    DATA_ASSET_PATH = "data_assets/sample_manufacturing_events.csv"
    with open(DATA_ASSET_PATH, "w") as f:
        f.write("event_id,machine_id,temperature_celsius\n")
        f.write("1,MCH-001,55\n")
        f.write("2,MCH-002,105\n") # This will fail the validation (temp > 100)
        f.write("3,MCH-003,30\n")
        
    # Since we cannot run PySpark directly in this environment, we will mock the successful execution
    # A real execution would look like this:
    # spark = SparkSession.builder.appName("DataQualityFramework").getOrCreate()
    # validation_results = run_data_validation(spark, EXPECTATION_SUITE_NAME, DATA_ASSET_PATH)
    # spark.stop()
    
    print("Mock validation run complete. Check the README for full details.")
