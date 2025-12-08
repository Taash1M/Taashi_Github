# Testing & Data Quality Standards

## Levels of Testing

1. **Unit Tests**  
   - Small functions (e.g., transformations, utilities).
   - Use `pytest` with clear, isolated test cases.

2. **Integration Tests**  
   - End-to-end flows (e.g., ingest → transform → publish).
   - Use realistic sample data and verify metrics or row counts.

3. **Data Quality Tests**  
   - Use Great Expectations or dbt tests.
   - Define expectations on nullability, uniqueness, ranges, referential integrity.

## Principles

- Tests must be **reproducible** and runnable in CI.
- Test failures should be **actionable**, not flaky noise.
- Data quality tests are part of **definition of done**.
