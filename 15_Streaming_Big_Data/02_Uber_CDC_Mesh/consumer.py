import time
import json
from utils_logger import setup_logger

logger = setup_logger("incentive_service")

# Local State Store (The "Mesh" Node)
# This service maintains its OWN copy of driver stats for calculating bonuses
driver_stats_cache = {}

def process_change_event(event):
    op_type = event.get("op")
    table = event.get("table")
    data = event.get("after")
    
    if not data: 
        return

    driver_id = data.get("driver_id")
    
    # Initialize cache if new driver
    if driver_id not in driver_stats_cache:
        driver_stats_cache[driver_id] = {"trips": 0, "rating": 5.0, "bonus_eligible": False}

    # LOGIC: Update local state based on DB change
    if table == "trips_ledger" and op_type == "u":
        driver_stats_cache[driver_id]["trips"] = data["trips_today"]
        logger.info(f"🔄 Syncing Trip Data: Driver {driver_id} has {data['trips_today']} trips.")
        
    elif table == "driver_profiles":
        if "rating" in data:
            driver_stats_cache[driver_id]["rating"] = data["rating"]
            logger.info(f"⭐ Rating Update: Driver {driver_id} is now {data['rating']}")

    # LOGIC: Check Business Rule (Real-time Incentive)
    # If trips > 15 AND rating > 4.8, unlock bonus
    stats = driver_stats_cache[driver_id]
    if stats["trips"] >= 15 and stats["rating"] >= 4.8:
        if not stats["bonus_eligible"]:
            logger.info(f"💰 BONUS UNLOCKED: Driver {driver_id} hit the daily target!")
            stats["bonus_eligible"] = True
            
def start_mesh_consumer():
    logger.info("Incentive Service (Mesh Node) Started...")
    logger.info("Listening for CDC events from Main Database...")
    
    # Simulation: We will generate events locally to verify the logic
    # In prod, this reads from Kafka
    logger.info("... Waiting for DB changes...")
    
    # Mock loop to show it working if run directly
    mock_events = [
        {"op": "c", "table": "driver_profiles", "after": {"driver_id": 99, "rating": 5.0}},
        {"op": "u", "table": "trips_ledger", "after": {"driver_id": 99, "trips_today": 10}},
        {"op": "u", "table": "trips_ledger", "after": {"driver_id": 99, "trips_today": 16}}, # Should trigger bonus
    ]
    
    for event in mock_events:
        time.sleep(1.5)
        process_change_event(event)

if __name__ == "__main__":
    start_mesh_consumer()