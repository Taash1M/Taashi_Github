"""Tests for the EventBus."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.event_bus import Event, EventBus


class TestEvent:
    def test_create_event(self):
        event = Event(event_type="test.created", source="test_agent")
        assert event.event_type == "test.created"
        assert event.source == "test_agent"
        assert event.event_id is not None
        assert event.timestamp > 0

    def test_event_with_payload(self):
        event = Event(
            event_type="task.completed",
            source="executor",
            payload={"result": "success", "count": 42}
        )
        assert event.payload["result"] == "success"
        assert event.payload["count"] == 42


class TestEventBus:
    def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []

        bus.subscribe("test.event", lambda e: received.append(e))
        bus.publish(Event(event_type="test.event", source="test"))

        assert len(received) == 1
        assert received[0].event_type == "test.event"

    def test_multiple_subscribers(self):
        bus = EventBus()
        results = {"a": 0, "b": 0}

        bus.subscribe("count", lambda e: results.__setitem__("a", results["a"] + 1))
        bus.subscribe("count", lambda e: results.__setitem__("b", results["b"] + 1))
        bus.publish(Event(event_type="count", source="test"))

        assert results["a"] == 1
        assert results["b"] == 1

    def test_wildcard_subscriber(self):
        bus = EventBus()
        all_events = []

        bus.subscribe("*", lambda e: all_events.append(e))
        bus.publish(Event(event_type="type_a", source="test"))
        bus.publish(Event(event_type="type_b", source="test"))

        assert len(all_events) == 2

    def test_no_cross_contamination(self):
        bus = EventBus()
        received_a = []
        received_b = []

        bus.subscribe("type_a", lambda e: received_a.append(e))
        bus.subscribe("type_b", lambda e: received_b.append(e))
        bus.publish(Event(event_type="type_a", source="test"))

        assert len(received_a) == 1
        assert len(received_b) == 0

    def test_event_history(self):
        bus = EventBus()
        bus.publish(Event(event_type="first", source="test"))
        bus.publish(Event(event_type="second", source="test"))

        history = bus.get_history()
        assert len(history) == 2
        assert history[0].event_type == "first"

    def test_history_filter_by_type(self):
        bus = EventBus()
        bus.publish(Event(event_type="keep", source="a"))
        bus.publish(Event(event_type="skip", source="b"))
        bus.publish(Event(event_type="keep", source="c"))

        filtered = bus.get_history(event_type="keep")
        assert len(filtered) == 2

    def test_history_filter_by_source(self):
        bus = EventBus()
        bus.publish(Event(event_type="test", source="agent_a"))
        bus.publish(Event(event_type="test", source="agent_b"))

        filtered = bus.get_history(source="agent_a")
        assert len(filtered) == 1

    def test_unsubscribe(self):
        bus = EventBus()
        received = []
        handler = lambda e: received.append(e)

        bus.subscribe("test", handler)
        bus.publish(Event(event_type="test", source="a"))
        assert len(received) == 1

        bus.unsubscribe("test", handler)
        bus.publish(Event(event_type="test", source="b"))
        assert len(received) == 1  # No new events

    def test_history_limit(self):
        bus = EventBus(max_history=5)
        for i in range(10):
            bus.publish(Event(event_type=f"event_{i}", source="test"))

        history = bus.get_history(limit=100)
        assert len(history) == 5

    def test_subscriber_count(self):
        bus = EventBus()
        bus.subscribe("a", lambda e: None)
        bus.subscribe("a", lambda e: None)
        bus.subscribe("b", lambda e: None)

        counts = bus.subscriber_count
        assert counts["a"] == 2
        assert counts["b"] == 1


    def test_handler_exception_does_not_crash_bus(self):
        """A failing handler should not prevent other handlers from running."""
        bus = EventBus()
        results = []

        def bad_handler(e):
            raise RuntimeError("handler crashed")

        def good_handler(e):
            results.append(e.event_type)

        bus.subscribe("test", bad_handler)
        bus.subscribe("test", good_handler)

        # Should not raise
        bus.publish(Event(event_type="test", source="test"))
        assert len(results) == 1

    def test_clear_history(self):
        bus = EventBus()
        bus.publish(Event(event_type="a", source="test"))
        bus.clear_history()
        assert len(bus.get_history()) == 0

    def test_empty_bus_returns_no_results(self):
        bus = EventBus()
        results = bus.publish(Event(event_type="nobody_listens", source="test"))
        assert results == []

    def test_correlation_id_propagation(self):
        bus = EventBus()
        received = []
        bus.subscribe("test", lambda e: received.append(e))
        bus.publish(Event(event_type="test", source="a", correlation_id="corr-123"))
        assert received[0].correlation_id == "corr-123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
