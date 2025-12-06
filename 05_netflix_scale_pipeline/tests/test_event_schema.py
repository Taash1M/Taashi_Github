import json
from src.producer_sim import generate_event

def test_event_has_expected_fields():
    e = generate_event()
    assert {"user_id", "event_type", "timestamp", "device"} <= set(e.keys())
