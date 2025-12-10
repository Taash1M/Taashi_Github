import time
import math
from utils_logger import setup_logger

logger = setup_logger("dispatch_engine")

# Simulated Database of Drivers (In-Memory)
drivers_db = {
    101: {"loc": (47.60, -122.33), "status": "IDLE"},
    102: {"loc": (47.62, -122.35), "status": "BUSY"},
    103: {"loc": (47.58, -122.30), "status": "IDLE"},
}

def calculate_distance(loc1, loc2):
    # Simple Euclidean distance
    return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)

def match_driver(order_id, order_loc):
    logger.info(f"Processing Order {order_id} at {order_loc}...")
    
    best_driver = None
    closest_dist = float('inf')
    
    for driver_id, data in drivers_db.items():
        if data['status'] == 'IDLE':
            dist = calculate_distance(order_loc, data['loc'])
            if dist < closest_dist:
                closest_dist = dist
                best_driver = driver_id
                
    if best_driver:
        logger.info(f"✅ MATCH: Assigned Driver {best_driver} (Distance: {closest_dist:.3f})")
        return True
    else:
        logger.warning(f"❌ FAILED: No available drivers for Order {order_id}")
        return False

def start_service():
    logger.info("Dispatch Service Online...")
    logger.info("Listening for Order Events (Simulated Loop)...")
    
    # Simulate receiving an order every few seconds
    mock_orders = [
        ("ORD-555", (47.601, -122.331)),
        ("ORD-777", (47.999, -122.999)), # Far away
        ("ORD-888", (47.581, -122.301))
    ]
    
    for order_id, loc in mock_orders:
        time.sleep(2)
        match_driver(order_id, loc)

if __name__ == "__main__":
    start_service()