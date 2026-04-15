# Design Decisions

## 1. Event-Driven Over Direct Calls

**Decision:** Agents communicate exclusively through an event bus, never by direct method calls.

**Why:** Decoupling agents from each other means we can add, remove, or reorder agents without changing any agent code. The orchestrator composes behavior through configuration, not inheritance. This follows the unix daemon philosophy: small, focused processes communicating through well-defined interfaces.

**Trade-off:** Slightly more complex to trace execution flow vs. direct calls. Mitigated by full event history and audit logging.

## 2. MCP-Style Tool Registry

**Decision:** Tools are registered with JSON schema definitions (name, description, input/output schemas) following the Model Context Protocol pattern.

**Why:** Standardized tool interfaces mean any agent can use any tool without coupling. The schema validation catches parameter errors early. This same pattern is used by Claude Code, LangChain, and other production agent frameworks.

**Trade-off:** More boilerplate per tool vs. just calling functions directly. But the validation, logging, and discoverability pay for themselves in production.

## 3. State Manager with Audit Trail

**Decision:** All shared state goes through a centralized StateManager that logs every mutation with agent attribution.

**Why:** In multi-agent systems, debugging requires knowing who changed what and when. The audit trail makes state transitions traceable. Snapshots enable checkpoint/restore for human-in-the-loop gates.

**Trade-off:** Memory overhead for mutation history. Mitigated by keeping only the last N mutations.

## 4. Mock LLM Responses for Demo

**Decision:** Agent logic uses rule-based templates and mock responses instead of real LLM calls.

**Why:** The project demonstrates the orchestration architecture, not LLM prompting. Running without API keys means anyone can clone and run immediately. The architecture has clear extension points where production code would call Azure OpenAI or Claude.

**Trade-off:** Demo output is synthetic rather than intelligent. But the patterns, interfaces, and architecture are production-ready.

## 5. Sandboxed Code Execution

**Decision:** The code execution tool runs in a restricted namespace with limited builtins.

**Why:** Executing agent-generated code is inherently risky. The sandbox prevents file system access, network calls, and dangerous operations. In production, this would use subprocess isolation with actual timeouts.

**Trade-off:** Some legitimate Python features are unavailable in the sandbox. Acceptable for the security guarantee.

## 6. Single-Process Architecture

**Decision:** All agents run in the same Python process with synchronous event dispatch.

**Why:** Simplicity for demo and testing. The event bus interface is the same whether dispatch is synchronous or async. Moving to multi-process or distributed execution is an infrastructure change, not an architecture change.

**Trade-off:** No true parallelism between agents. In production, use async dispatch or a message queue (Redis, RabbitMQ, Azure Service Bus).
