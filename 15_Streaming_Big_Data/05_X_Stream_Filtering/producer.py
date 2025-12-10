import time
import json
import random
from utils_logger import setup_logger

logger = setup_logger("firehose_producer")

# Mock Data Sources
TOPICS = ["Politics", "Sports", "K-Pop", "Crypto", "Tech", "Memes", "News"]
HASHTAGS = ["#Bitcoin", "#AI", "#TaylorSwift", "#SuperBowl", "#Python", "#Election2024", "#Cats"]
USERS = [f"@user_{i}" for i in range(1000, 9999)]

def generate_tweet():
    topic = random.choice(TOPICS)
    hashtag = random.choice(HASHTAGS)
    
    # Simulate a tweet structure
    return {
        "id": random.getrandbits(64),
        "user": random.choice(USERS),
        "text": f"Just saw this crazy update about {topic}! {hashtag}",
        "topic": topic,
        "is_verified": random.choice([True, False]),
        "timestamp_ms": int(time.time() * 1000)
    }

def start_firehose():
    logger.info("Starting X (Twitter) Firehose Simulation...")
    logger.info("Warning: High Volume Stream Initiated 🌊")
    
    while True:
        # Generate a burst of tweets to simulate high throughput
        burst_size = random.randint(1, 10)
        
        for _ in range(burst_size):
            tweet = generate_tweet()
            # We log minimal info here because the volume is too high to read
            logger.info(f"Generated Tweet: [{tweet['topic']}] {tweet['text'][:30]}...")
            
        # Very short sleep to simulate 50+ tweets per second
        time.sleep(0.1)

if __name__ == "__main__":
    start_firehose()