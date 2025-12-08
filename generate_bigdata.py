import os
import json
import random
import uuid
import datetime

# --- Configuration ---
# Target Directory relative to the script location
TARGET_DIR = os.path.join("Implementation Code", "bigdata")
RECORDS_PER_USECASE = 5000  # "Sufficient" data for testing pipelines

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_timestamp(offset_seconds=0):
    """Returns a timestamp string ISO 8601"""
    dt = datetime.datetime.now() - datetime.timedelta(seconds=offset_seconds)
    return dt.isoformat()

# --- Use Case 1: DoorDash Logistics (Late Events) ---
def generate_doordash_data(output_file):
    print(f"Generating DoorDash data -> {output_file}")
    statuses = ["ORDER_PLACED", "DASHER_CONFIRMED", "PICKED_UP", "DELIVERED"]
    
    with open(output_file, 'w') as f:
        for _ in range(RECORDS_PER_USECASE):
            order_id = str(uuid.uuid4())[:8]
            # Simulate "Event Time" vs "Processing Time" lag
            # 10% of data will be "late" (older than 10 minutes)
            is_late = random.random() < 0.1
            lag_seconds = random.randint(600, 3600) if is_late else random.randint(1, 60)
            
            event = {
                "event_uuid": str(uuid.uuid4()),
                "order_id": order_id,
                "status": random.choice(statuses),
                "driver_lat": round(random.uniform(47.5, 47.7), 6), # Seattleish coords
                "driver_lon": round(random.uniform(-122.4, -122.2), 6),
                "event_timestamp": get_timestamp(offset_seconds=lag_seconds), # The 'real' time event happened
                "ingestion_timestamp": get_timestamp(), # When we saw it
                "is_late_event": is_late # Helper flag for your sanity checks later
            }
            f.write(json.dumps(event) + "\n")

# --- Use Case 2: Uber CDC (Schema Evolution) ---
def generate_uber_cdc_data(output_file):
    print(f"Generating Uber CDC data -> {output_file}")
    ops = ["c", "u", "u", "d"] # create, update, delete
    
    with open(output_file, 'w') as f:
        for _ in range(RECORDS_PER_USECASE):
            op = random.choice(ops)
            user_id = random.randint(1000, 9999)
            
            # CDC 'Envelope' structure similar to Debezium
            record = {
                "op": op,
                "ts_ms": int(datetime.datetime.now().timestamp() * 1000),
                "before": None if op == 'c' else {
                    "user_id": user_id,
                    "ride_status": "REQUESTED",
                    "fare_estimate": round(random.uniform(10.0, 50.0), 2)
                },
                "after": None if op == 'd' else {
                    "user_id": user_id,
                    "ride_status": "COMPLETED" if op == 'u' else "REQUESTED",
                    "fare_estimate": round(random.uniform(10.0, 50.0), 2),
                    "surge_multiplier": round(random.uniform(1.0, 2.5), 1) # Schema evolution field
                }
            }
            f.write(json.dumps(record) + "\n")

# --- Use Case 3: Netflix Keystone (Routing) ---
def generate_netflix_data(output_file):
    print(f"Generating Netflix Keystone data -> {output_file}")
    event_types = ["play_start", "buffer_underrun", "pause", "stop", "heartbeat"]
    regions = ["us-west-1", "us-east-1", "eu-central-1", "ap-northeast-1"]
    
    with open(output_file, 'w') as f:
        for _ in range(RECORDS_PER_USECASE):
            event = {
                "trace_id": str(uuid.uuid4()),
                "event_type": random.choice(event_types),
                "region": random.choice(regions),
                "device_info": {
                    "device_id": str(uuid.uuid4())[:12],
                    "os_version": f"v{random.randint(10,15)}.{random.randint(0,5)}"
                },
                "routing_tag": "priority_high" if random.random() < 0.2 else "standard",
                "payload_size_bytes": random.randint(256, 4096)
            }
            f.write(json.dumps(event) + "\n")

# --- Use Case 4: Snapchat (Real-time ML) ---
def generate_snapchat_data(output_file):
    print(f"Generating Snapchat ML data -> {output_file}")
    
    with open(output_file, 'w') as f:
        for _ in range(RECORDS_PER_USECASE):
            # Simulating features for engagement prediction
            event = {
                "snap_id": str(uuid.uuid4()),
                "viewer_id": random.randint(100000, 999999),
                "sender_id": random.randint(100000, 999999),
                "view_duration_ms": int(random.expovariate(1/5000) + 100), # Exponential distribution
                "interaction_type": random.choice(["view", "swipe_up", "screenshot", "reply"]),
                "filter_used": random.choice([None, "dog_ears", "glitch", "beauty_v2"]),
                "timestamp": get_timestamp()
            }
            f.write(json.dumps(event) + "\n")

# --- Use Case 5: X/Twitter (Stream Filtering) ---
def generate_x_data(output_file):
    print(f"Generating X (Twitter) data -> {output_file}")
    hashtags_pool = ["#tech", "#crypto", "#ai", "#news", "#sports", "#funny", "#politics"]
    words = ["amazing", "terrible", "just saw", "unbelievable", "check this out", "breaking", "lol"]
    
    with open(output_file, 'w') as f:
        for _ in range(RECORDS_PER_USECASE):
            # Create a mock tweet
            txt = f"{random.choice(words)} {random.choice(words)} {random.choice(hashtags_pool)}"
            
            tweet = {
                "tweet_id": str(uuid.uuid4().int)[:16],
                "user_id": f"user_{random.randint(1, 1000)}",
                "text": txt,
                "hashtags": [tag for tag in hashtags_pool if tag in txt],
                "lang": "en",
                "is_verified": random.random() < 0.05,
                "created_at": get_timestamp()
            }
            f.write(json.dumps(tweet) + "\n")

def main():
    print("🚀 Starting Synthetic Data Generation...")
    
    # 1. Ensure 'bigdata' root folder exists
    ensure_dir(TARGET_DIR)
    
    # 2. Define sub-paths and generate
    tasks = [
        ("doordash_logistics.jsonl", generate_doordash_data),
        ("uber_cdc.jsonl", generate_uber_cdc_data),
        ("netflix_routing.jsonl", generate_netflix_data),
        ("snapchat_ml.jsonl", generate_snapchat_data),
        ("x_stream.jsonl", generate_x_data)
    ]
    
    for filename, func in tasks:
        # Create a specific folder for each dataset if you prefer, or keep them as files in bigdata
        # Here we dump them as files directly into bigdata/ for simplicity of access
        full_path = os.path.join(TARGET_DIR, filename)
        func(full_path)
    
    print(f"\n✅ Done! Generated {RECORDS_PER_USECASE * 5} records total.")
    print(f"📂 Location: {os.path.abspath(TARGET_DIR)}")

if __name__ == "__main__":
    main()