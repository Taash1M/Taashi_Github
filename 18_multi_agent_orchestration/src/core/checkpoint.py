"""
Checkpoint — Human-in-the-loop gates for agent pipelines.

Provides configurable pause points where a human reviewer can
inspect state, approve/reject, or modify data before the pipeline
continues. Essential for high-stakes workflows where autonomous
execution needs guardrails.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CheckpointDecision(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    SKIP = "skip"


@dataclass
class CheckpointResult:
    """Result of a checkpoint review."""
    decision: CheckpointDecision
    reviewer: str
    comments: str = ""
    modifications: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class CheckpointConfig:
    """Configuration for a checkpoint gate."""
    name: str
    description: str
    required_keys: list[str] = field(default_factory=list)
    auto_approve: bool = False
    timeout_seconds: float | None = None


class CheckpointGate:
    """
    Human-in-the-loop checkpoint gate.

    In production, this would integrate with a UI or messaging system.
    For demo purposes, it supports both auto-approve mode (for testing)
    and a programmatic review interface.
    """

    def __init__(self):
        self._history: list[tuple[str, CheckpointResult]] = []
        self._pending_review: dict[str, dict] = {}

    def request_review(self, config: CheckpointConfig,
                       state: dict[str, Any]) -> str:
        """
        Submit state for human review at a checkpoint.

        Returns a review_id for tracking. In auto-approve mode,
        the review completes immediately.
        """
        review_id = f"review_{config.name}_{int(time.time())}"

        # Validate required keys are present
        missing = [k for k in config.required_keys if k not in state]
        if missing:
            raise ValueError(
                f"Checkpoint '{config.name}' requires keys: {missing}"
            )

        if config.auto_approve:
            result = CheckpointResult(
                decision=CheckpointDecision.APPROVE,
                reviewer="auto",
                comments="Auto-approved per checkpoint config"
            )
            self._history.append((review_id, result))
            return review_id

        # Store for manual review
        self._pending_review[review_id] = {
            "config": config,
            "state_snapshot": {k: state.get(k) for k in config.required_keys},
            "submitted_at": time.time()
        }
        return review_id

    def submit_review(self, review_id: str,
                      result: CheckpointResult) -> bool:
        """Submit a review decision for a pending checkpoint."""
        if review_id not in self._pending_review:
            return False

        del self._pending_review[review_id]
        self._history.append((review_id, result))
        return True

    def get_review_result(self, review_id: str) -> CheckpointResult | None:
        """Get the result of a completed review."""
        for rid, result in self._history:
            if rid == review_id:
                return result
        return None

    def is_pending(self, review_id: str) -> bool:
        """Check if a review is still pending."""
        return review_id in self._pending_review

    def get_pending(self) -> dict[str, dict]:
        """Get all pending reviews."""
        return dict(self._pending_review)

    @property
    def history(self) -> list[tuple[str, CheckpointResult]]:
        """Full review history."""
        return list(self._history)
