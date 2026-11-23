# Startup Due Diligence MAS — State, Persistence and Observability

Status: working draft · Updated: 2026-11-23

Related documents: [Architecture](architecture.md) · [Open Points](open_points.md) · [Benchmark](benchmark_registry.md) · [REST API](rest_api.md)

## Shared Domain Models and LangGraph State

| Model | Contents |
| --- | --- |
| `CompanyInfo` | General information about the target company, supplied by the user. |
| `CompanyProfile` | Profile split into Generic, Team, Tech and Commercial sections. |
| `AnalysisReview` | Reviewer output: completeness score (0–10), missing items, summary. |

All are Pydantic models used by both frameworks. LangGraph keeps them in the graph state with the fields needed for transitions (Profiler iterations, consolidated analysis, review data).

### Concurrent State Updates

The LangGraph fan-out runs Tech, Commercial and Team in parallel through `Send`, and several nodes update the same profile. The profile field is declared with `Annotated` and the custom `merge_profile` reducer, which applies incoming updates and keeps existing data. Other fields written concurrently use reducers the same way.

## LangGraph Persistence and Resume

A SQLite checkpointer saves the graph state. The graph pauses at the interrupt and resumes later with the same `thread_id`, even after a restart, as long as the database is available.

| Data | Purpose |
| --- | --- |
| Graph checkpoints | State by `thread_id`, to resume the graph. |
| Tracer state | Carries elapsed time and usage across the interrupt. |
| Execution records | Name, status, timing, tokens, cost and the analysis preview shown during review. |

`thread_id` identifies the checkpoint thread; the tracing identifier refers to the observability trace. Persistent execution support for CrewAI is still to do.

## Tracing, File Logging and Execution Metrics

| Capability | LangGraph | CrewAI |
| --- | --- | --- |
| Tracing | LangSmith (Due Diligence project): graph nodes, LLM and tool calls. | CrewAI built-in tracing. |
| File logging | Shared logging function. | Same function. |
| Metrics | Duration, tokens and cost in execution records. | Duration, tokens and cost. |

Measured values are in the [benchmark registry](benchmark_registry.md#1-execution-overview).
