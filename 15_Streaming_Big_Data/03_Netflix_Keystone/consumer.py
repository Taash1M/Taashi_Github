import time
import json
from utils_logger import setup_logger

logger = setup_logger("keystone_aggregator")

# In-Memory Session Store (The "State" of the Stream)
active_sessions = {}

def process_event(event):
    uid = event["user_id"]
    e_type = event["event_type"]
    title = event["title"]
    
    # 1. Handle New Sessions
    if e_type == "session_start":
        active_sessions[uid] = {
            "title": title, 
            "start_time": event["timestamp_ms"],
            "buffer_count": 0
        }
        logger.info(f"▶️  START: {uid} began watching '{title}'")

    # 2. Handle Buffering (QoE Detection)
    elif e_type == "buffering_start":
        if uid in active_sessions:
            active_sessions[uid]["buffer_count"] += 1
            count = active_sessions[uid]["buffer_count"]
            logger.warning(f"⚠️  BUFFERING: {uid} experiencing lag on '{title}' (Count: {count})")
            
            # Simple Logic: If buffer > 3 times, flag as Critical Issue
            if count >= 3:
                logger.error(f"🚨 CRITICAL QoE ALERT: {uid} has poor connection. Downgrade bitrate requested.")

    # 3. Handle Heartbeats (View Duration)
    elif e_type == "playback_heartbeat":
        pass # In a real system, we accumulate "seconds watched" here

    # 4. Handle Stop (Session Finalization)
    elif e_type == "session_end":
        if uid in active_sessions:
            session = active_sessions.pop(uid)
            duration_sec = (event["timestamp_ms"] - session["start_time"]) / 1000
            logger.info(f"⏹️  STOP: {uid} finished '{session['title']}'. Total Duration: {duration_sec:.1f}s")

def start_consumer():
    logger.info("Keystone Processing Engine Started...")
    logger.info("Aggregating viewing sessions in real-time...")
    
    # Simulation Loop
    # In reality, this loop consumes from Kafka
    logger.info("... Listening for telemetry events ...")
    
    # Mock sequence to demonstrate logic
    mock_sequence = [
        {"event_type": "session_start", "user_id": "u1", "title": "Stranger Things", "timestamp_ms": 1000},
        {"event_type": "playback_heartbeat", "user_id": "u1", "title": "Stranger Things", "timestamp_ms": 2000},
        {"event_type": "buffering_start", "user_id": "u1", "title": "Stranger Things", "timestamp_ms": 3000},
        {"event_type": "buffering_start", "user_id": "u1", "title": "Stranger Things", "timestamp_ms": 4000},
        {"event_type": "buffering_start", "user_id": "u1", "title": "Stranger Things", "timestamp_ms": 5000}, # Should trigger ALERT
        {"event_type": "session_end", "user_id": "u1", "title": "Stranger Things", "timestamp_ms": 8000}
    ]
    
    for evt in mock_sequence:
        time.sleep(1.0)
        process_event(evt)

if __name__ == "__main__":
    start_consumer()