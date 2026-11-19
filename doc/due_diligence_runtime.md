# Startup Due Diligence MAS — State, Persistence and Observability

Status: working draft · Updated: 2026-11-19

Related documents · [Architecture](due_diligence_architecture.md) · [Overview](due_diligence_overview.md) · [Open Points](due_diligence_open_points.md) · [Benchmark](due_diligence_benchmark_registry.md)

## Shared Domain Models and LangGraph State

| Model | Contents |
| --- | --- |
| `CompanyInfo` | General information supplied by the user about the target company. |
| `CompanyProfile` | Company profile split into Generic, Team, Tech and Commercial sections. |

Both frameworks use these models, which inherit from Pydantic's `BaseModel`. LangGraph keeps them in the graph state alongside the fields needed for workflow transitions, including the Profiler iteration data, the consolidated analysis and the review data.

### Concurrent State Updates

Parallel execution and concurrent state updates are explicit requirements. The LangGraph fan-out uses `Send` to run Tech, Commercial and Team in parallel. Multiple nodes can return updates to the same company profile. The profile field uses `Annotated` to associate it with the custom `merge_profile` reducer, which applies incoming deltas and preserves existing data outside those updates. Other state fields also use reducers declared with `Annotated` where concurrent writes need to be combined.

## LangGraph Persistence and Resume

The project uses a SQLite-backed checkpointer to persist graph state for human review and recovery. At the interrupt, the graph can pause and later resume using the same `thread_id`. If the application process restarts or crashes, the saved checkpoint can still be used to resume as long as its database is available.

SQLite stores three kinds of data for the workflow.

| Data | What is stored and why |
| --- | --- |
| Graph checkpoints | The checkpointer stores state by `thread_id` so the graph can resume from its saved state. |
| Tracer state | A dedicated table stores the tracing callback's state across the interrupt. The callback wraps graph execution before the interrupt and after resume so elapsed-time and usage data can be carried across both segments. |
| Execution records | A dedicated table stores the execution name and status, timing, total tokens, monetary cost, and supporting data such as the analysis preview shown during human review. |

The graph's `thread_id` identifies the checkpoint thread. A tracing identifier refers to the observability trace. Persistent execution support for CrewAI is still to do.

## Tracing, File Logging and Execution Metrics

| Capability | LangGraph | CrewAI |
| --- | --- | --- |
| Tracing | The Due Diligence project in LangSmith uses API-key access. Traces cover graph nodes, LLM calls and tool calls. | CrewAI tracing provides analogous visibility into its execution. |
| File logging | A shared function writes log files for supplementary diagnostics or backup. | Uses the same file-logging function. |
| Benchmark metrics | Execution records capture total duration, total token usage and monetary cost. | Execution metrics include total duration, total token usage and monetary cost. |

The benchmark compares these metrics per execution. The [benchmark registry](due_diligence_benchmark_registry.md#esecuzioni) records the measured values when available.
