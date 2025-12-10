import time
import json
import random
from utils_logger import setup_logger

logger = setup_logger("keystone_edge_producer")

# Mock Catalog
SHOWS = ["Stranger Things", "The Crown", "Squid Game", "Black Mirror"]
USERS = [f"user_{i}" for i in range(1001, 1010)]

def generate_event():
    user = random.choice(USERS)
    show = random.choice(SHOWS)
    
    # Event Probability Distribution
    # 5% Start, 5% Stop, 80% Heartbeat (Playing), 10% Error/Buffer
    rand = random.random()
    
    if rand < 0.05:
        event_type = "session_start"
    elif rand < 0.10:
        event_type = "session_end"
    elif rand < 0.20:
        event_type = "buffering_start"
    else:
        event_type = "playback_heartbeat"

    return {
        "event_type": event_type,
        "user_id": user,
        "title": show,
        "device": random.choice(["SmartTV", "Mobile", "Web"]),
        "timestamp_ms": int(time.time() * 1000),
        "bitrate_kbps": random.choice([4000, 5800, 12000]) if event_type == "playback_heartbeat" else 0
    }

def start_streaming():
    logger.info("Starting Netflix Keystone Simulation...")
    logger.info("Emitting telemetry from client devices...")
    
    while True:
        # Simulate high volume by generating batch events
        events = [generate_event() for _ in range(random.randint(1, 5))]
        
        for event in events:
            logger.info(f"📡 Ingest: {json.dumps(event)}")
            time.sleep(0.2) # Fast stream

if __name__ == "__main__":
    start_streaming()