# 02. Production-Grade Data Quality Framework (Great Expectations & Spark)

## 💡 Project Overview: Operational Excellence and Reliability

This project presents a robust, scalable, and automated data quality framework designed for high-volume, real-time data streams. It directly addresses the need for **99.5% reliability** and **60% reduction in data quality incidents** mentioned in your resume, providing a concrete, reusable code base.

The framework integrates:
*   **Great Expectations (GE):** For defining, validating, and documenting data expectations (tests).
*   **Apache Spark:** For distributed, high-performance execution of validation checks on large datasets.
*   **CI/CD Integration:** Designed to be run as a mandatory step in a CI/CD pipeline (e.g., GitHub Actions) before data is promoted from Silver to Gold layers.

## ⚙️ Framework Structure

The framework is structured to separate concerns:
*   `expectations/`: Stores JSON files defining the data quality rules (Expectation Suites).
*   `data_assets/`: Contains sample data for testing and demonstration.
*   `validation_scripts/`: Python scripts for connecting to the data source, loading the Expectation Suite, and running the validation.

## 💻 Code Example: `validation_script.py`

This script demonstrates how to programmatically load data, apply a predefined Expectation Suite, and generate a validation report.

```python
# validation_script.py

from great_expectations.core import ExpectationSuite, ExpectationConfiguration
from great_expectations.data_context import DataContext
from great_expectations.dataset import SparkDFDataset
from pyspark.sql import SparkSession

# --- Configuration ---
EXPECTATION_SUITE_NAME = "manufacturing_events_suite"
DATA_ASSET_PATH = "data_assets/sample_manufacturing_events.csv"

def run_data_validation(spark: SparkSession, suite_name: str, data_path: str):
    """
    Loads data and runs the Great Expectations validation suite.
    """
    print(f"Loading data from: {data_path}")
    df = spark.read.csv(data_path, header=True, inferSchema=True)
    
    # Create a Great Expectations Spark Dataset
    ge_df = SparkDFDataset(df)
    
    # --- Define Expectations Programmatically (Mocking the GE Suite) ---
    # In a real scenario, this would be loaded from a JSON file
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
    # Initialize Spark Session (Mock)
    spark = SparkSession.builder.appName("DataQualityFramework").getOrCreate()
    
    # Create a dummy data file for the script to read
    with open(DATA_ASSET_PATH, "w") as f:
        f.write("event_id,machine_id,temperature_celsius\n")
        f.write("1,MCH-001,55\n")
        f.write("2,MCH-002,105\n") # This will fail the validation (temp > 100)
        f.write("3,MCH-003,30\n")
        
    validation_results = run_data_validation(spark, EXPECTATION_SUITE_NAME, DATA_ASSET_PATH)
    
    # Stop Spark Session (Mock)
    spark.stop()
```
