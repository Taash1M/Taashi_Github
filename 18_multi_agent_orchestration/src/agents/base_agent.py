"""
Base Agent — Abstract base class for all pipeline agents.

Every agent follows the same lifecycle:
1. Receive an event with task context
2. Read shared state
3. Execute logic (optionally using tools)
4. Update state with results
5. Publish completion event

Agents are single-purpose components. They don't know about other
agents — only about events and state.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..core.event_bus import Event, EventBus
from ..core.state_manager import StateManager
from ..tools.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for an agent instance."""
    name: str
    role: str
    description: str
    subscriptions: list[str] = field(default_factory=list)
    max_tool_calls: int = 10
    timeout_seconds: float = 300.0


@dataclass
class AgentResult:
    """Result of an agent execution."""
    agent_name: str
    success: bool
    output: Any = None
    error: str | None = None
    tool_calls: int = 0
    duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        return {
            "agent": self.agent_name,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "tool_calls": self.tool_calls,
            "duration": round(self.duration_seconds, 2),
        }


class BaseAgent(ABC):
    """
    Abstract base class for pipeline agents.

    Subclasses implement `execute()` with their specific logic.
    The base class handles event subscription, state access,
    tool invocation, and result publishing.
    """

    def __init__(self, config: AgentConfig, event_bus: EventBus,
                 state: StateManager, tools: ToolRegistry):
        self.config = config
        self.event_bus = event_bus
        self.state = state
        self.tools = tools
        self._tool_call_count = 0

        # Subscribe to configured event types
        for event_type in config.subscriptions:
            event_bus.subscribe(event_type, self._handle_event)

    @abstractmethod
    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent's logic on a task.

        Args:
            task: Dict containing the task context from the triggering event.

        Returns:
            Dict containing the agent's output.
        """
        pass

    def use_tool(self, tool_name: str, params: dict | None = None,
                 max_retries: int = 2, backoff_base: float = 0.5) -> ToolResult:
        """Invoke a tool through the registry with call counting and retry logic.

        Retries transient failures with exponential backoff. Gives up after
        max_retries attempts, returning the last failure result.
        """
        if self._tool_call_count >= self.config.max_tool_calls:
            logger.warning(
                "tool_limit_exceeded agent=%s tool=%s limit=%d",
                self.config.name, tool_name, self.config.max_tool_calls,
            )
            return ToolResult(
                tool_name=tool_name, success=False,
                error=f"Agent '{self.config.name}' exceeded max tool calls "
                      f"({self.config.max_tool_calls})"
            )

        last_result = None
        for attempt in range(max_retries + 1):
            self._tool_call_count += 1
            logger.info(
                "tool_invoke agent=%s tool=%s attempt=%d params=%s",
                self.config.name, tool_name, attempt + 1, list((params or {}).keys()),
            )
            last_result = self.tools.invoke(tool_name, params)
            if last_result.success:
                return last_result
            # Don't retry if tool not found or missing params (non-transient)
            if last_result.error and ("not found" in last_result.error
                                       or "Missing required" in last_result.error):
                logger.error("tool_failed_permanent agent=%s tool=%s error=%s",
                             self.config.name, tool_name, last_result.error)
                return last_result
            if attempt < max_retries:
                wait = backoff_base * (2 ** attempt)
                logger.warning(
                    "tool_retry agent=%s tool=%s attempt=%d wait=%.1fs error=%s",
                    self.config.name, tool_name, attempt + 1, wait, last_result.error,
                )
                time.sleep(wait)

        logger.error("tool_failed_all_retries agent=%s tool=%s retries=%d",
                     self.config.name, tool_name, max_retries)
        return last_result

    def read_state(self, key: str, default: Any = None) -> Any:
        """Read from shared state."""
        return self.state.get(key, default)

    def write_state(self, key: str, value: Any) -> None:
        """Write to shared state with agent attribution."""
        self.state.set(key, value, agent=self.config.name)

    def publish(self, event_type: str, payload: dict | None = None,
                correlation_id: str | None = None) -> Event:
        """Publish an event to the bus."""
        event = Event(
            event_type=event_type,
            source=self.config.name,
            payload=payload or {},
            correlation_id=correlation_id,
        )
        self.event_bus.publish(event)
        return event

    def _handle_event(self, event: Event) -> AgentResult:
        """Internal event handler — wraps execute() with lifecycle management."""
        self._tool_call_count = 0
        start = time.time()

        logger.info(
            "agent_start agent=%s event=%s correlation=%s",
            self.config.name, event.event_type,
            event.correlation_id or event.event_id,
        )

        try:
            output = self.execute(event.payload)
            duration = time.time() - start

            result = AgentResult(
                agent_name=self.config.name,
                success=True,
                output=output,
                tool_calls=self._tool_call_count,
                duration_seconds=duration,
            )

            logger.info(
                "agent_completed agent=%s duration=%.2fs tools=%d",
                self.config.name, duration, self._tool_call_count,
            )

            # Publish completion event
            self.publish(
                f"{self.config.name}.completed",
                payload={"result": result.to_dict()},
                correlation_id=event.correlation_id or event.event_id,
            )

        except Exception as e:
            duration = time.time() - start
            result = AgentResult(
                agent_name=self.config.name,
                success=False,
                error=str(e),
                tool_calls=self._tool_call_count,
                duration_seconds=duration,
            )

            logger.error(
                "agent_failed agent=%s duration=%.2fs error=%s",
                self.config.name, duration, str(e),
            )

            self.publish(
                f"{self.config.name}.failed",
                payload={"error": str(e), "result": result.to_dict()},
                correlation_id=event.correlation_id or event.event_id,
            )

        return result

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.config.name}, role={self.config.role})"
