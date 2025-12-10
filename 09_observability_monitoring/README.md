# Observability & Monitoring (Metrics, Logs, Traces Concept)

This project demonstrates how I think about **observability** for data platforms:

- Application-level metrics (request counts, latencies)
- Structured logging
- Hooks for Prometheus/Grafana (conceptually)

## Components

- `src/metrics_demo.py`: Simple app with Prometheus-style metrics and logs.

This is not meant to spin up full infra, but to show how I structure code to be observable.
