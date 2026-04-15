"""
Event Bus — Publish/subscribe message passing between agents.

Agents communicate exclusively through events, never by direct calls.
This decouples agent logic from orchestration flow, enabling modular
composition via configuration rather than code changes.
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """An immutable event published by an agent."""
    event_type: str
    source: str
    payload: dict = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    correlation_id: str | None = None

    def __repr__(self):
        return f"Event({self.event_type}, source={self.source}, id={self.event_id})"


class EventBus:
    """
    In-process pub/sub event bus.

    Agents subscribe to event types and receive callbacks when events
    of that type are published. Supports wildcard subscriptions ('*')
    and event history for replay/debugging.
    """

    def __init__(self, max_history: int = 1000):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._history: list[Event] = []
        self._max_history = max_history

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Subscribe a handler to an event type. Use '*' for all events."""
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove a handler from an event type."""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def publish(self, event: Event) -> list[Any]:
        """
        Publish an event to all subscribers.

        Returns a list of handler results for synchronous processing.
        Wildcard subscribers ('*') receive all events.
        """
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        results = []
        subscribers = (
            self._subscribers.get(event.event_type, [])
            + self._subscribers.get("*", [])
        )
        logger.debug(
            "event_published type=%s source=%s id=%s subscribers=%d",
            event.event_type, event.source, event.event_id, len(subscribers),
        )
        for handler in subscribers:
            try:
                results.append(handler(event))
            except Exception as exc:
                logger.error(
                    "handler_exception type=%s handler=%s error=%s",
                    event.event_type, getattr(handler, "__qualname__", str(handler)), exc,
                )
                results.append(None)

        return results

    def get_history(self, event_type: str | None = None,
                    source: str | None = None,
                    limit: int = 50) -> list[Event]:
        """Query event history with optional filters."""
        events = self._history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if source:
            events = [e for e in events if e.source == source]
        return events[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()

    @property
    def subscriber_count(self) -> dict[str, int]:
        """Count of subscribers per event type."""
        return {k: len(v) for k, v in self._subscribers.items() if v}
