"""
Dataflow pipeline: Ingest manufacturing CSV -> Bronze (JSON in GCS).

Usage example (from local or GCS CSV):

    python ingest_to_bronze.py \
      --project=<YOUR_PROJECT_ID> \
      --region=us-central1 \
      --runner=DataflowRunner \
      --temp_location=gs://<YOUR_BUCKET>/dataflow/temp \
      --staging_location=gs://<YOUR_BUCKET>/dataflow/staging \
      --input=gs://<YOUR_BUCKET>/sample_data/manufacturing_events.csv \
      --output_prefix=gs://<YOUR_BUCKET>/manufacturing_events/bronze/events

This writes files like:
  gs://<YOUR_BUCKET>/manufacturing_events/bronze/events-00000-of-00005.json
"""

import argparse
import csv
import json

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions


class CsvToDict(beam.DoFn):
    def __init__(self, has_header=True):
        self.has_header = has_header

    def process(self, element):
        # element is a line of CSV. We use the header from side input if present.
        # This is a simplified example; in production, consider proper schema handling.
        line = element
        # The header handling here is naive; in many patterns you'd load header separately.
        # For this demo we assume CSV with header is pre-parsed or we read via TextIO + csv.
        raise NotImplementedError("This template is for illustrative structure; replace with your own CSV parsing logic.")


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV path (GCS).")
    parser.add_argument("--output_prefix", required=True, help="Output prefix in GCS for Bronze JSON.")
    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(
        pipeline_args,
        save_main_session=True,
        streaming=False,
    )

    # For practical usage, you'll likely use beam.io.ReadFromText + csv.DictReader in a DoFn.
    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "ReadCSV" >> beam.io.ReadFromText(known_args.input, skip_header_lines=1)
            | "ParseCSV" >> beam.Map(lambda line: dict(zip(
                ["timestamp", "device_id", "facility_id", "temperature", "pressure", "vibration", "status", "production_rate", "quality_score"],
                next(csv.reader([line]))
            )))
            | "ToJSON" >> beam.Map(json.dumps)
            | "WriteJSON" >> beam.io.WriteToText(
                known_args.output_prefix,
                file_name_suffix=".json",
                shard_name_template="-SSSSS-of-NNNNN",
            )
        )


if __name__ == "__main__":
    run()
