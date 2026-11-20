# Startup Due Diligence MAS — Open Points

Status: working draft · Updated: 2026-11-19

Related documents: [Overview](due_diligence_overview.md) · [Architecture](due_diligence_architecture.md) · [Benchmark](due_diligence_benchmark_registry.md) · [State, persistence and observability](due_diligence_runtime.md)

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
| Reproduction (2026-11-20) | CrewAI 1.15.41, `openai/gpt-4o-mini`, Analyst Crew (hierarchical, 3 async specialist tasks): the crew failed after 333 s with `Task execution failed: Executor is already running. Cannot invoke the same executor instance concurrently.` The flow method `analyze_company` failed with it |
| Probable cause | In the hierarchical process the manager executes every task, so the async tasks invoke the same manager executor instance in parallel |
| Switch | `ANALYST_ASYNC=false` runs the specialist tasks sequentially, to compare with the async run |

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

Version 2 supplies each specialist with the general profile and explicitly selected domain context. Validate the handoff with traces and compare repeated retrieval calls against Version 1.

## OP-03 — Is Supervisor Orchestration Necessary?

Version 1 uses a manager for delegation across analysis. Version 2 scopes the manager to profiling quality and bounded retrieval retries. LangGraph uses a project-defined Supervisor node and code-based routing. It reviews the company profile, returning gaps and research feedback for up to three profiling passes, and reviews the completeness of the consolidated analysis before the human interrupt. Evaluate whether supervisor-led profiling improves evidence coverage or accuracy enough to justify its token and latency cost. Compare against explicit profiling orchestration on the same inputs and record execution errors and repeated retrieval calls alongside memo quality.

## OP-04 — Automated Debate Eligibility Check

The proposed check scores whether the analysis contains enough evidence to support Debate. The illustrative rule makes scores above 6/10 eligible and routes scores of 6/10 or lower to the analysis-only export. The current CrewAI Flow exposes three routes through human review. In LangGraph, the Supervisor already returns a completeness score from 1 to 10 and a review summary after aggregation. The router then interrupts and the user chooses whether to run Debate or go directly to the Memo Writer.

| Decision | Open question |
| --- | --- |
| Scoring rubric | Which criteria and weights determine whether the evidence supports Debate? |
| Threshold | Which production cutoff and equality behavior work on benchmark cases? |
| CrewAI human review | When should the proposed CrewAI score be computed, and how should it affect the user’s decision? |
| CrewAI direct memo | Should the direct Memo Writer route remain available when the proposed eligibility check blocks Debate? |

## Remaining Evaluation

| Topic | Next step |
| --- | --- |
| CrewAI variants | Compare parallel execution, context handoff, execution errors and output quality on matching runs. |
| Reproducibility | Record framework versions, model identifiers, selected route, total duration, tokens and monetary cost for each benchmark run. |
| CrewAI persistence | Implement persistent execution support. LangGraph currently uses SQLite for checkpoints, tracer state and execution records. |
| Framework choice | Compare CrewAI and LangGraph on matching inputs and evaluation criteria. |
