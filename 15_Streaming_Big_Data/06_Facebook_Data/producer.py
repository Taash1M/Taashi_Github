import time
import json
import random
from utils_logger import setup_logger

logger = setup_logger("fb_interaction_stream")

# Mock Data: 100 Active Posts
POST_IDS = [f"post_{i}" for i in range(1000, 1100)]
USER_IDS = [f"user_{i}" for i in range(5000, 9999)]
REACTIONS = ["LIKE", "LOVE", "HAHA", "WOW", "SAD", "ANGRY"]

def generate_interaction():
    # Simulate "Viral" behavior: Some posts get 80% of the traffic
    if random.random() < 0.8:
        post_id = random.choice(POST_IDS[:10]) # Top 10 viral posts
    else:
        post_id = random.choice(POST_IDS)

    return {
        "event_type": "interaction",
        "post_id": post_id,
        "user_id": random.choice(USER_IDS),
        "reaction": random.choice(REACTIONS),
        "timestamp_ms": int(time.time() * 1000)
    }

def start_stream():
    logger.info("Starting Facebook Interaction Stream...")
    logger.info("Simulating global user engagement...")

    while True:
        # Simulate burst traffic (e.g., a live video event)
        burst = random.randint(5, 20)
        
        for _ in range(burst):
            event = generate_interaction()
            # Log sampling to avoid console spam
            if random.random() < 0.1:
                logger.info(f"👍 Interaction: {event['user_id']} reacted {event['reaction']} to {event['post_id']}")
        
        time.sleep(0.5) # 2 bursts per second

if __name__ == "__main__":
    start_stream()