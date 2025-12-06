# Data Quality Framework (Great Expectations + pytest)

This project demonstrates a **data quality framework** similar to those I've implemented in 
production: combining Great Expectations, pytest, and CI/CD to ensure trustworthy, governed data.

## Key Components

- `src/validate_orders.py`: Entry point to run Great Expectations validations.
- `great_expectations/expectations/orders_expectation_suite.json`: Example expectation suite.
- `tests/test_basic_quality.py`: pytest-based unit tests for data rules.
- `.github/workflows/ci.yml`: CI pipeline running tests and validations.

## How to Run (Local Demo)

1. Install Python dependencies:
   ```bash
   pip install great-expectations pytest pandas
   ```
2. Run data validation:
   ```bash
   python src/validate_orders.py
   ```
3. Run tests:
   ```bash
   pytest tests
   ```

This framework illustrates my approach to **establishing a culture of data trust and governance**. As a manager, I enforce data quality programmatically and continuously, ensuring that engineering efforts directly support business reliability and decision-making.
