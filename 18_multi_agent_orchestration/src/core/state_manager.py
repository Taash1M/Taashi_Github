"""
State Manager — Persistent state across agent handoffs.

Maintains a shared state dict that agents read from and write to.
Supports snapshots for checkpoint/restore and full audit trail
of every state mutation.
"""

import copy
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StateMutation:
    """Record of a single state change."""
    agent: str
    key: str
    old_value: Any
    new_value: Any
    timestamp: float = field(default_factory=time.time)


class StateManager:
    """
    Shared state store with snapshot/restore and audit trail.

    Agents access state through get/set methods. Every mutation is
    logged for debugging and compliance. Snapshots enable checkpoint
    gates where a human can inspect state before the pipeline continues.
    """

    def __init__(self):
        self._state: dict[str, Any] = {}
        self._mutations: list[StateMutation] = []
        self._snapshots: dict[str, dict[str, Any]] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from state."""
        return self._state.get(key, default)

    def set(self, key: str, value: Any, agent: str = "system") -> None:
        """Set a value in state with audit logging."""
        old_value = self._state.get(key)
        self._state[key] = value
        self._mutations.append(StateMutation(
            agent=agent, key=key,
            old_value=old_value, new_value=value
        ))

    def get_all(self) -> dict[str, Any]:
        """Get a copy of the full state."""
        return copy.deepcopy(self._state)

    def snapshot(self, name: str) -> None:
        """Save a named snapshot of current state."""
        self._snapshots[name] = copy.deepcopy(self._state)

    def restore(self, name: str) -> bool:
        """Restore state from a named snapshot. Returns False if not found."""
        if name not in self._snapshots:
            return False
        self._state = copy.deepcopy(self._snapshots[name])
        self._mutations.append(StateMutation(
            agent="system", key="__restore__",
            old_value=name, new_value="restored"
        ))
        return True

    def list_snapshots(self) -> list[str]:
        """List available snapshot names."""
        return list(self._snapshots.keys())

    def get_mutations(self, agent: str | None = None,
                      key: str | None = None,
                      limit: int = 50) -> list[StateMutation]:
        """Query mutation history with optional filters."""
        mutations = self._mutations
        if agent:
            mutations = [m for m in mutations if m.agent == agent]
        if key:
            mutations = [m for m in mutations if m.key == key]
        return mutations[-limit:]

    def clear(self) -> None:
        """Clear all state (but preserve snapshots)."""
        self._state.clear()

    @property
    def keys(self) -> list[str]:
        """List all state keys."""
        return list(self._state.keys())
