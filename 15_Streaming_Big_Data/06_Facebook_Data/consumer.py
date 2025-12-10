import time
from collections import defaultdict
from utils_logger import setup_logger

logger = setup_logger("viral_content_engine")

# In-Memory State: Tracks reactions per post in the last window
# Format: {post_id: count}
post_velocity = defaultdict(int)

VIRAL_THRESHOLD = 15 # Interactions per check cycle

def analyze_traffic(batch_events):
    # 1. Aggregate current batch
    for event in batch_events:
        pid = event["post_id"]
        post_velocity[pid] += 1
        
    # 2. Check for Viral Spikes
    for pid, count in post_velocity.items():
        if count > VIRAL_THRESHOLD:
            logger.info(f"🚀 VIRAL TREND DETECTED: {pid} has {count} interactions/sec! Pushing to Feed.")
        elif count > 5:
            logger.info(f"📈 Rising: {pid} is gaining traction ({count} interactions).")
            
    # 3. Decay/Reset (Simulating a sliding window)
    post_velocity.clear()

def start_engine():
    logger.info("Viral Detection Engine Started...")
    logger.info("Monitoring Post Velocity...")
    
    # Simulated Consumption Loop
    while True:
        # Mocking a batch of incoming events from the 'producer'
        # In real life, this reads from Kafka/Kinesis
        mock_batch = [{"post_id": "post_1001"} for _ in range(20)] # Simulate viral post
        
        analyze_traffic(mock_batch)
        time.sleep(2.0)

if __name__ == "__main__":
    start_engine()