import time
import json
import random
from utils_logger import setup_logger

logger = setup_logger("producer")

# Mock locations (Seattle Lat/Lon roughly)
RESTAURANTS = [
    {"name": "Burger King", "loc": (47.6062, -122.3321)},
    {"name": "Sushi Zen", "loc": (47.6100, -122.3400)},
    {"name": "Pizza Hut", "loc": (47.5900, -122.3200)}
]

def generate_driver_ping(driver_id):
    # Simulate a driver moving slightly
    lat = 47.60 + random.uniform(-0.05, 0.05)
    lon = -122.33 + random.uniform(-0.05, 0.05)
    return {
        "event_type": "driver_update",
        "driver_id": driver_id,
        "location": (lat, lon),
        "status": random.choice(["IDLE", "BUSY", "IDLE"]) # Higher chance of IDLE for demo
    }

def generate_order():
    restaurant = random.choice(RESTAURANTS)
    return {
        "event_type": "order_ready",
        "order_id": f"ORD-{random.randint(1000, 9999)}",
        "restaurant": restaurant["name"],
        "location": restaurant["loc"],
        "timestamp": time.time()
    }

def start_stream():
    logger.info("Starting DoorDash Simulation Stream...")
    logger.info("Press Ctrl+C to stop.")
    
    while True:
        # 70% chance of driver update, 30% chance of new order
        if random.random() < 0.7:
            event = generate_driver_ping(driver_id=random.randint(1, 5))
        else:
            event = generate_order()
            
        logger.info(f"Emitted: {json.dumps(event)}")
        
        # Stream speed (faster for demo purposes)
        time.sleep(1.5)

if __name__ == "__main__":
    start_stream()