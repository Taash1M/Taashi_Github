import json
import time
import random
from pathlib import Path

def generate_event():
    return {
        "user_id": random.randint(1, 1000),
        "event_type": random.choice(["play", "pause", "stop"]),
        "timestamp": int(time.time()),
        "device": random.choice(["mobile", "web", "tv"])
    }

def main():
    out_path = Path("events_log.jsonl")
    with out_path.open("a", encoding="utf-8") as f:
        for _ in range(100):
            event = generate_event()
            f.write(json.dumps(event) + "\n")
    print(f"Wrote 100 events to {out_path}")

if __name__ == "__main__":
    main()
