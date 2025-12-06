# Netflix-Scale Streaming Pipeline (Kafka → Spark → Lake)

This project illustrates a **streaming data pipeline** pattern aligned with 
large-scale environments like Netflix:

- Kafka-like message ingestion (simulated)
- Spark-based micro-batch processing
- Aggregations for analytics

## Components

- `src/producer_sim.py`: Simulates event production.
- `src/spark_streaming_job.py`: Spark structured streaming job (pseudo-code).
- `tests/test_event_schema.py`: Validates schema assumptions.

This repo is about showing distributed systems thinking, not full infra spin-up.
