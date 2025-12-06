import pandas as pd
from great_expectations.dataset import PandasDataset
from pathlib import Path

class OrdersDataset(PandasDataset):
    _expectation_suite_name = "orders_expectation_suite"

def load_orders_csv(path: str) -> OrdersDataset:
    df = pd.read_csv(path)
    return OrdersDataset(df)

def main():
    data_path = Path("data") / "orders_sample.csv"
    ds = load_orders_csv(str(data_path))

    ds.expect_column_values_to_not_be_null("order_id")
    ds.expect_column_values_to_not_be_null("customer_id")
    ds.expect_column_values_to_be_between("order_total", min_value=0)
    ds.expect_column_values_to_match_regex("currency", "^[A-Z]{3}$")

    results = ds.validate()
    print(results)

    if not results["success"]:
        raise SystemExit("Data quality checks failed.")
    else:
        print("All data quality checks passed.")

if __name__ == "__main__":
    main()
