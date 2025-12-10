
import json

def run_mock_pipeline():
    print("Starting Dataflow Simulation...")

    # ==========================================
    # BRONZE LAYER (Raw Stream)
    # ==========================================
    print("--- Bronze Layer: Ingesting Pub/Sub ---")
    with open("../data/gcp_clickstream.json", "r") as f:
        raw_stream = f.readlines()[:20] # Simulating unbounded stream
    
    # ==========================================
    # SILVER LAYER (Parsed & Watermarked)
    # ==========================================
    print("--- Silver Layer: Parsing & Watermarking ---")
    parsed_events = []
    for line in raw_stream:
        evt = json.loads(line)
        # In a real pipeline, we assign Event Time here for Watermarks
        parsed_events.append(evt)
    print(f"[System] Watermark Logic Applied: Allowing 10min lateness.")

    # ==========================================
    # GOLD LAYER (Sessionized Analytics)
    # ==========================================
    print("--- Gold Layer: Session Window Aggregation ---")
    user_sessions = {}
    for event in parsed_events:
        u = event['user']
        # Logic: If gap > 5 mins, new session. (Simplified for demo)
        user_sessions[u] = user_sessions.get(u, 0) + 1
        
    print("--- Executive Summary: Gold Layer Sessions ---")
    for u, count in list(user_sessions.items())[:5]:
        print(f"User {u} | Actions in Session: {count}")

if __name__ == "__main__":
    run_mock_pipeline()
