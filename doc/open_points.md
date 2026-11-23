# Startup Due Diligence MAS — Open Points

Status: working draft · Updated: 2026-11-23

Related documents: [Architecture](architecture.md) · [Benchmark](benchmark_registry.md) · [State, persistence and observability](runtime.md) · [REST API](rest_api.md)

Project observations, not verified framework-wide limitations.

## OP-01 — Overlapping Delegation During Asynchronous Execution

**Confirmed on CrewAI v1 (discarded). v2 avoids it by design.**

- **Setup:** hierarchical process with async specialist tasks.
- **Error:** `Executor is already running. Cannot invoke the same executor instance concurrently.` (CrewAI 1.15.41, `openai/gpt-4o-mini`, failed after 333 s on 2026-11-20).
- **Cause:** the manager executes every task, so the async tasks call the same executor in parallel.
- **Check:** `ANALYST_ASYNC=false` runs the specialists sequentially.

A stronger model is not expected to fix it.

## OP-02 — Non-Deterministic Context Handoff

**Confirmed on CrewAI v1 (discarded). v2 passes context explicitly.**

- **Expected:** a task receives the full output of its declared context.
- **Observed:** the manager passes an extreme summary, so specialists repeat retrieval calls.
- **Prompt instructions** do not make the transfer deterministic.

## OP-03 — Is Supervisor Orchestration Necessary?

Does supervisor-led profiling improve evidence coverage enough to justify its token and latency cost? Compare with profiling without a supervisor on the same inputs, recording errors, repeated retrieval calls and memo quality.

## OP-04 — Score-Based Debate Gating

Both frameworks already produce a completeness score; today the user sees it and chooses `proceed` or `end`. No automatic gate exists. To decide:

- **Threshold:** which cutoff makes the analysis eligible for Debate (illustrative: above 6/10), and how to treat equality.
- **Rubric:** is the 0–10 completeness rubric enough for Debate?
- **Override:** can the user override the gate, and does `end` stay available?
- **Follow-up tasks:** should a low score wait for the created tasks?
