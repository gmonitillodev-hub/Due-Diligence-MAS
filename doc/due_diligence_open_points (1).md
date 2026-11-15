# Startup Due Diligence MAS — Open Points

Status: working draft · Updated: 2026-11-15

Related documents: [Overview](due_diligence_overview.md) · [Architecture](due_diligence_architecture.md)

These notes record project observations and hypotheses, not independently verified framework-wide limitations. Concluding the discussion of a point does not mean the technical issue is resolved.

## OP-01 — Overlapping Delegation During Asynchronous Execution

| Aspect | Finding |
| --- | --- |
| Status | Observed; unresolved |
| Configuration | CrewAI hierarchical process with asynchronous task execution |
| Observed behavior | The manager attempts additional delegations while other executions are already running, producing execution errors |
| Impact | Noisy execution with rejected or overlapping attempts |
| Token behavior reported | CrewAI rejects the conflicting attempt before another LLM call; that rejected attempt therefore does not add an LLM call in the observed path |
| Hypothesis | A more capable model might reduce inappropriate delegation attempts; this has not been demonstrated |
| Missing detail | Exact model identifier and CrewAI version |

The token observation applies to the rejected attempt, not to all manager decisions or the overall workflow cost.

Suggested verification: retain traces, identify the reused executor or agent instance, and compare model configurations under the same workload. A stronger model should not be assumed to fix an execution-level concurrency issue.

## OP-02 — Non-Deterministic Context Handoff

| Aspect | Finding |
| --- | --- |
| Status | Observed non-determinism; unresolved |
| Expected contract | Task X+1 receives the full output of task X when that output is its declared context |
| Observed behavior | The manager chooses what context to transmit, frequently passing an extreme summary instead of the complete analysis |
| Impact | Specialist agents repeat retrieval calls to recover information already collected |
| Prompt-only mitigation | Instructions to forward the exact output do not establish a deterministic transfer guarantee |

For the observed architecture, non-determinism is an established property of the LLM-mediated handoff, not merely a hypothetical risk.

Suggested direction: pass required outputs through explicit application-managed state or task inputs, and reserve the manager for coordination or quality decisions. This is a proposal to evaluate, not an implemented fix.

## Pending Documentation and Decisions

| Topic | Next step |
| --- | --- |
| CrewAI Version 2 | Document the changed analysis stage and compare it with Version 1 |
| Profiling | Specify where the Company Profiler runs in Version 1 and how its output reaches downstream tasks |
| Human-in-the-loop | Document checkpoints, review inputs and continuation behavior |
| Reproducibility | Record exact framework versions and model identifiers |
| Supervisor scope | Evaluate where LLM supervision adds value while preserving required data transfers |
| Framework choice | Implement LangGraph and compare both frameworks against the same requirements |
