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