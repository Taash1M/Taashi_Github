import os

base_dir = "/workspaces/Taashi_Github/Implementation Code/15_Streaming_Big_Data/06_Facebook_Data"

# 1. CONSUMER CODE (Viral Detector)
consumer_code = """
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
"""

# 2. UTILS CODE
utils_code = """
import logging
import sys

def setup_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
"""

# Write files
def write_file(name, content):
    path = os.path.join(base_dir, name)
    with open(path, "w") as f:
        f.write(content.strip())
    print(f"✅ Generated: {path}")

write_file("consumer.py", consumer_code)
write_file("utils_logger.py", utils_code)
write_file("requirements.txt", "pandas\nnumpy")
write_file(".env", "ENV=PROD")
