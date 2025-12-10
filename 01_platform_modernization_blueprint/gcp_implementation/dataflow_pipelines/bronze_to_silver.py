"""
Dataflow pipeline: Bronze (JSON) -> Silver (Parquet).

Reads JSON lines from:
  gs://<YOUR_BUCKET>/manufacturing_events/bronze/...

Writes partitioned Parquet to:
  gs://<YOUR_BUCKET>/manufacturing_events/silver/
"""

import argparse
import json
from datetime import datetime

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.internal.clients import bigquery


def parse_json(line):
    record = json.loads(line)
    # Basic casting and normalization; enhance as needed
    def safe_float(v):
        try:
            return float(v)
        except Exception:
            return None

    def safe_int(v):
        try:
            return int(v)
        except Exception:
            return None

    ts_str = record.get("timestamp")
    try:
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        ts = None

    return {
        "timestamp": ts_str,
        "device_id": (record.get("device_id") or "").strip().upper(),
        "facility_id": (record.get("facility_id") or "").strip().upper(),
        "temperature_c": safe_float(record.get("temperature")),
        "pressure_kpa": safe_float(record.get("pressure")),
        "vibration_mm_s": safe_float(record.get("vibration")),
        "status": record.get("status"),
        "production_rate": safe_int(record.get("production_rate")),
        "quality_score": safe_float(record.get("quality_score")),
        "process_date": ts.date().isoformat() if ts else None,
        "processed_timestamp": datetime.now(datetime.timezone.utc).isoformat(),
    }


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_prefix", required=True, help="Input Bronze JSON prefix (GCS).")
    parser.add_argument("--output_prefix", required=True, help="Output Silver Parquet prefix (GCS).")
    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(
        pipeline_args,
        save_main_session=True,
        streaming=False,
    )

    with beam.Pipeline(options=pipeline_options) as p:
        records = (
            p
            | "ReadBronzeJSON" >> beam.io.ReadFromText(known_args.input_prefix + "*.json")
            | "ParseJSON" >> beam.Map(parse_json)
        )

        # In practice, to write Parquet you'll use a ParquetIO sink or bq load.
        # Here we demonstrate writing to BigQuery as Silver; adjust to Parquet if needed.

        table_schema = {
            "fields": [
                {"name": "timestamp", "type": "TIMESTAMP"},
                {"name": "device_id", "type": "STRING"},
                {"name": "facility_id", "type": "STRING"},
                {"name": "temperature_c", "type": "FLOAT"},
                {"name": "pressure_kpa", "type": "FLOAT"},
                {"name": "vibration_mm_s", "type": "FLOAT"},
                {"name": "status", "type": "STRING"},
                {"name": "production_rate", "type": "INTEGER"},
                {"name": "quality_score", "type": "FLOAT"},
                {"name": "process_date", "type": "DATE"},
                {"name": "processed_timestamp", "type": "TIMESTAMP"},
            ]
        }

        # For simplicity, treat this as "Silver in BigQuery" rather than Parquet in GCS.
        # If you want pure file-based Silver, replace this with a Parquet sink.
        (
            records
            | "WriteToSilverBQ" >> beam.io.WriteToBigQuery(
                table=lambda elem: "your_project.your_dataset.silver_manufacturing_events",
                schema=table_schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )


if __name__ == "__main__":
    run()
