import time
import json
from utils_logger import setup_logger

logger = setup_logger("topic_filter_service")

# CONFIGURATION: What we actually care about
INTEREST_KEYWORDS = ["#AI", "#Python", "Tech"]
BLOCKED_USERS = ["@user_1234", "@bot_999"]

def filter_process(tweet):
    # 1. Spam/Block Filter
    if tweet['user'] in BLOCKED_USERS:
        return # Drop silently
    
    # 2. Content Filter (The "Where" Clause)
    # We only want Tech and AI tweets. Everything else is "Noise" to this service.
    
    is_interesting = any(k in tweet['text'] for k in INTEREST_KEYWORDS) or tweet['topic'] == "Tech"
    
    if is_interesting:
        # PROCESSED: This is the data we keep/store/analyze
        logger.info(f"✅ MATCH FOUND: {tweet['user']} says: '{tweet['text']}'")
        # In a real app, we would write this to a specific Kafka topic like 'tech-stream'
    else:
        # IGNORED: This represents data we pay to ingest but discard
        # We log at DEBUG level (or not at all) to save space
        # Here we print a faint message just to show it was checked
        pass 

def start_filter_engine():
    logger.info("Filter Engine Online. Listening for: " + str(INTEREST_KEYWORDS))
    
    # Simulation: We will generate mock data internally to demonstrate the filtering
    # because piping the actual producer output in a simple shell is hard to visualize.
    
    logger.info("... Connecting to Firehose ...")
    
    # Mock loop representing the incoming stream
    mock_data = [
        {"user": "@user_1", "topic": "K-Pop", "text": "I love BTS! #Music"},
        {"user": "@dev_guy", "topic": "Tech", "text": "Learning #Python is awesome for #AI"}, # MATCH
        {"user": "@sports_fan", "topic": "Sports", "text": "Did you see that goal? #Soccer"},
        {"user": "@crypto_bro", "topic": "Crypto", "text": "Bitcoin to the moon! #Bitcoin"},
        {"user": "@ai_researcher", "topic": "Tech", "text": "New LLM models are changing everything #AI"}, # MATCH
    ]
    
    while True:
        for tweet in mock_data:
            time.sleep(1.0) # Slow down for readability
            filter_process(tweet)

if __name__ == "__main__":
    start_filter_engine()