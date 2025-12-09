import os

# DEFINITION: Target Directory
base_dir = "/workspaces/Taashi_Github/Implementation Code/15_Streaming_Big_Data/04_Snapchat_RealTimeML"

# Helper to write files
def write_file(filename, content):
    os.makedirs(base_dir, exist_ok=True)
    path = os.path.join(base_dir, filename)
    with open(path, "w") as f:
        f.write(content.strip())
    print(f"✅ Created/Updated: {filename}")

# ========================================================
# 1. CREATE PRODUCER (Simulates Camera/Face Data)
# ========================================================
producer_code = """
import time
import json
import random
from utils_logger import setup_logger

logger = setup_logger("camera_stream")

def generate_face_mesh(frame_id):
    # Simulating 3D coordinates of facial landmarks (Eyes, Nose, Mouth)
    # Moving slightly every frame to simulate head movement
    base_x = 500 + (frame_id % 50) 
    return {
        "event_type": "frame_data",
        "frame_id": frame_id,
        "timestamp_ms": int(time.time() * 1000),
        "device_id": "iphone_13_pro_max",
        "filter_id": "dog_ears_v2",
        "landmarks": {
            "left_eye": [base_x - 30, 400],
            "right_eye": [base_x + 30, 400],
            "nose_tip": [base_x, 450]
        }
    }

def start_camera_stream():
    logger.info("Starting Video Telemetry Stream (30 FPS)...")
    
    frame_count = 0
    while True:
        frame_count += 1
        data = generate_face_mesh(frame_count)
        
        logger.info(f"📸 Frame #{frame_count} sent to ML Engine.")
        
        # Simulate 30 FPS (Frames Per Second) -> ~0.033s delay
        time.sleep(0.033)

if __name__ == "__main__":
    start_camera_stream()
"""

# ========================================================
# 2. CREATE CONSUMER (ML Inference Service)
# ========================================================
consumer_code = """
import time
import json
import random
from utils_logger import setup_logger

logger = setup_logger("ml_inference_engine")

# Thresholds
MAX_LATENCY_MS = 33 # If processing takes > 33ms, we drop the frame (lag)

def run_inference_model(landmarks):
    # Simulate complex matrix math (ML Model)
    # 90% of the time it's fast (10ms). 10% of the time it lags (50ms).
    if random.random() < 0.9:
        processing_time = 0.010 
    else:
        processing_time = 0.050 
        
    time.sleep(processing_time)
    
    # Calculate AR Overlay Coordinates (Simple Offset)
    nose = landmarks["nose_tip"]
    return {
        "asset": "dog_nose_3d",
        "position": [nose[0], nose[1] - 5], # Slightly above nose tip
        "scale": 1.2
    }, processing_time

def process_frame(event):
    start_ts = int(time.time() * 1000)
    frame_id = event["frame_id"]
    
    # 1. Run ML Model
    overlay_data, duration_s = run_inference_model(event["landmarks"])
    
    # 2. Calculate Total Latency (Network + Compute)
    # We simulate network time by comparing event timestamp to now
    network_latency = start_ts - event["timestamp_ms"] 
    compute_latency = int(duration_s * 1000)
    total_lag = network_latency + compute_latency
    
    # 3. Check for "Drift" or Lag
    if total_lag > MAX_LATENCY_MS:
        logger.warning(f"⚠️  LAG DETECTED: Frame #{frame_id} took {total_lag}ms (Threshold: {MAX_LATENCY_MS}ms) - DROPPING FRAME")
    else:
        logger.info(f"✨ Rendered Frame #{frame_id} | Latency: {total_lag}ms | Overlay at {overlay_data['position']}")

def start_ml_service():
    logger.info("ML Inference Service Started...")
    logger.info("Waiting for video frames...")
    
    # Simulated Loop to act as Consumer
    # In prod, this reads from Kafka/gRPC stream
    
    # Let's simulate incoming frames arriving slightly irregularly
    current_frame = 0
    while True:
        current_frame += 1
        # Mock payload
        mock_event = {
            "frame_id": current_frame,
            "timestamp_ms": int(time.time() * 1000) - random.randint(5, 15), # Simulate network delay
            "landmarks": {"nose_tip": [500, 450]}
        }
        
        process_frame(mock_event)
        
        # Service runs slightly faster than producer to catch up
        time.sleep(0.030)

if __name__ == "__main__":
    start_ml_service()
"""

# ========================================================
# 3. UTILS & CONFIG
# ========================================================
logger_code = """
import logging
import sys

def setup_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        # Detailed millisecond logging is crucial for this use case
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
"""

write_file("producer.py", producer_code)
write_file("consumer.py", consumer_code)
write_file("utils_logger.py", logger_code)
write_file("requirements.txt", "numpy\npandas")
write_file(".env", "MODEL_VERSION=v2.4\nLATENCY_THRESHOLD_MS=33")

print("\\n✅ Snapchat Real-Time ML Logic injected successfully.")