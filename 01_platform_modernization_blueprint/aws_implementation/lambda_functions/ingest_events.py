"""
Lambda function to ingest manufacturing events into Bronze S3 layer.

This function expects either:
- Kinesis events with JSON payloads, or
- Direct "event" with JSON records for testing.

It writes a CSV file into the Bronze prefix in S3.
"""

import csv
import json
from datetime import datetime
from io import StringIO

import boto3


s3 = boto3.client("s3")

# Replace with your real bucket name, e.g. "data-platform-123456789012-bronze"
BRONZE_BUCKET = "data-platform-<ACCOUNT_ID>-bronze"
BRONZE_PREFIX = "manufacturing_events/bronze/"


def _records_from_kinesis(event):
    import base64
    records = []
    for record in event.get("Records", []):
        kinesis = record.get("kinesis")
        if not kinesis:
            continue
        payload = base64.b64decode(kinesis["data"]).decode("utf-8")
        records.append(json.loads(payload))
    return records


def _records_from_direct_event(event):
    if isinstance(event, list):
        return event
    if isinstance(event, dict) and "records" in event:
        return event["records"]
    return [event]


def lambda_handler(event, context):
    try:
        if "Records" in event and "kinesis" in event["Records"][0]:
            records = _records_from_kinesis(event)
        else:
            records = _records_from_direct_event(event)

        if not records:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No records to ingest"})
            }

        # Convert to CSV
        from datetime import timezone
        ts = datetime.now(timezone.utc)
        date_prefix = ts.strftime("%Y/%m/%d")
        hour = ts.strftime("%H")

        csv_buffer = StringIO()
        fieldnames = list(records[0].keys())
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

        key = f"{BRONZE_PREFIX}{date_prefix}/{hour}/events_{ts.strftime('%Y%m%d%H%M%S')}.csv"

        s3.put_object(
            Bucket=BRONZE_BUCKET,
            Key=key,
            Body=csv_buffer.getvalue().encode("utf-8"),
            ContentType="text/csv",
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"Ingested {len(records)} records", "location": f"s3://{BRONZE_BUCKET}/{key}"}
            ),
        }
    except Exception as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(exc)})
        }
