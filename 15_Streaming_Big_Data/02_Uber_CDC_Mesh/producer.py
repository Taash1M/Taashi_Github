import time
import json
import random
from utils_logger import setup_logger

logger = setup_logger("cdc_producer")

# Mock Database Table: Drivers
# We simulate a "Write-Ahead Log" (WAL) stream
DRIVER_IDS = [101, 102, 103, 104, 105]

def generate_wal_event():
    driver_id = random.choice(DRIVER_IDS)
    
    # 60% chance of a Trip Update (Ride completed)
    # 30% chance of a Rating Change
    # 10% chance of a New Driver Signup (Insert)
    rand_val = random.random()
    
    if rand_val < 0.6:
        # UPDATE operation: Trip Completed
        return {
            "op": "u", # 'u' for Update
            "table": "trips_ledger",
            "ts_ms": int(time.time() * 1000),
            "before": None, 
            "after": {
                "driver_id": driver_id,
                "trips_today": random.randint(1, 20),
                "earnings": round(random.uniform(20.0, 500.0), 2)
            }
        }
    elif rand_val < 0.9:
        # UPDATE operation: Rating Change
        return {
            "op": "u",
            "table": "driver_profiles",
            "ts_ms": int(time.time() * 1000),
            "after": {
                "driver_id": driver_id,
                "rating": round(random.uniform(4.2, 5.0), 2)
            }
        }
    else:
        # CREATE operation: New Driver
        new_id = random.randint(200, 999)
        return {
            "op": "c", # 'c' for Create
            "table": "driver_profiles",
            "ts_ms": int(time.time() * 1000),
            "after": {
                "driver_id": new_id,
                "name": "New Driver",
                "status": "onboarding"
            }
        }

def start_cdc_stream():
    logger.info("Starting Postgres CDC Simulator (Debezium Style)...")
    logger.info("Streaming database changes to 'cdc-events' topic...")
    
    while True:
        event = generate_wal_event()
        # Log it like a database change event
        logger.info(f"CDC Event: {json.dumps(event)}")
        time.sleep(1)

if __name__ == "__main__":
    start_cdc_stream()