from pathlib import Path
import pandas as pd

def test_orders_have_positive_totals():
    data_path = Path("data") / "orders_sample.csv"
    df = pd.read_csv(data_path)
    assert (df["order_total"] >= 0).all(), "Order totals must be non-negative"
