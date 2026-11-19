# Startup Due Diligence MAS — Architecture

Status: working draft · Updated: 2026-11-19

Related documents: [Overview](due_diligence_overview.md) · [Open Points](due_diligence_open_points.md) · [Benchmark](due_diligence_benchmark_registry.md) · [State, persistence and observability](due_diligence_runtime.md)

## Shared Agent Architecture

Each agent is defined in a concrete class that inherits from `BaseAgent`, which provides the shared methods. The concrete class manages the agent's description and task instructions. Their text is defined in shared constants so CrewAI and LangGraph use the same definitions. A framework-specific adapter maps those definitions into the corresponding runtime inputs.

| Shared definition | CrewAI adapter | LangGraph adapter |
| --- | --- | --- |
| Agent description | Agent description and backstory | System prompt |
| Task instructions | CrewAI task | Human message |

## CrewAI — Version 1

A CrewAI Flow coordinates three crews and collects the startup name, website, sector and additional information from the user.

| Order | Stage | Configuration | Output |
| --- | --- | --- | --- |
| 1 | User input | Managed by the Flow | Startup information |
| 2 | Analysis Crew | Hierarchical; manager agent with an LLM, Company Profiler, and Tech, Team and Commercial agents | Intermediate analysis report |
| 3 | Debate Crew | Sequential: Formatter, Pro Extractor, Contra Extractor, Judge | Debate findings and judgment |
| 4 | Memo Writer Crew | One agent, one task | Structured, formatted final memo |

### Flow Diagram — Version 1

The Flow owns orchestration and the human decision. Arrows inside the Analysis Crew represent manager-mediated delegation and returned results, not guaranteed parallel scheduling.

```mermaid
flowchart TD
    Input["User input"] --> Manager
    subgraph Analysis["Analysis Crew — hierarchical"]
        Manager["Manager agent"]
        Profiler["Company Profiler"]
        Tech["Tech Analyst"]
        Commercial["Commercial Analyst"]
        Team["Team Analyst"]
        Manager <-->|"Delegation / results"| Profiler
        Manager <-->|"Delegation / results"| Tech
        Manager <-->|"Delegation / results"| Commercial
        Manager <-->|"Delegation / results"| Team
    end
    Manager --> Report["Intermediate analysis report"]
    Report --> Review{"Human review in Flow"}
    Review -->|"Export analysis"| AnalysisOut["Analysis-only deliverable"]
    Review -->|"Skip Debate"| Writer["Memo Writer Crew"]
    Review -->|"Run Debate"| Debate["Debate Crew — sequential"]
    Debate --> Writer
    Writer --> Memo["Formatted memo"]
```

Asynchronous execution within the hierarchical crew produced the overlapping delegation and context-transfer issues recorded in OP-01 and OP-02. Debate runs Formatter, Pro Extractor, Contra Extractor and Judge in order.

### Analysis Crew

The manager coordinates task execution and delegation among the specialist agents, then structures the intermediate analysis report.

Parallelism is required. Testing of hierarchical orchestration combined with asynchronous tasks exposed overlapping delegation attempts; see [OP-01](due_diligence_open_points.md#op-01--overlapping-delegation-during-asynchronous-execution).

A separate issue concerns the context supplied by the manager during delegation; see [OP-02](due_diligence_open_points.md#op-02--non-deterministic-context-handoff).

### Debate Crew — Shared by Both Versions

The four agents execute sequentially in this order:

1. Formatter.
2. Pro Extractor.
3. Contra Extractor.
4. Judge.

This crew does not change between the two CrewAI versions.

### Memo Writer Crew — Shared by Both Versions

A single agent executes a single task, consolidating the initial company profile and individual specialist analyses, plus Debate output and Judge findings when Debate has run.

It produces the final synthesis and formatted due diligence memo. This crew does not change between versions.

### Profiling and Human Review

Profiling is part of the initial Analysis Crew in Version 1 and is extracted into a separate crew in Version 2.

In CrewAI, the Flow handles human review after Analysis and before Debate.

The Flow displays a preview of the analysts' report and asks whether to proceed. The Debate Crew is initialized only when the user chooses to run it.

| User decision | Route | Result |
| --- | --- | --- |
| Analysis is sufficient as-is, or evidence is insufficient for a meaningful debate | Export the Analysis output | Analysis-only deliverable |
| A formatted memo is wanted without Debate | Skip Debate; invoke Memo Writer directly | Memo based on profiling and specialist analyses |
| Debate is useful and supported by sufficient information | Run Debate, then Memo Writer | Memo including debate findings |

The purpose is to let the user inspect the analysis before spending more tokens and time. Skipping Debate avoids its execution cost; directly exporting Analysis also avoids final memo-generation cost. The direct Memo Writer route still incurs memo-generation cost.

The stage tables show the full path; downstream execution is conditional on this decision.

### CrewAI Proposed Automation — Not Yet Implemented

Introduce an information-sufficiency check at the entry to the Debate stage, before running the full Debate Crew. It would score the analysts' output for whether enough evidence exists to support a useful debate.

Under the illustrative rule, a score above 6/10 makes the report eligible for Debate. A score of 6/10 or lower routes to the analysis-only output. Evidence sufficiency determines eligibility. Whether Debate would add value is a separate decision. The rubric, production threshold, placement relative to human review and any override remain open. For the decisions still needed, see [OP-04](due_diligence_open_points.md#op-04--automated-debate-eligibility-check).

## CrewAI — Version 2

An alternative version was introduced following problems combining hierarchical orchestration with parallel execution.

The Flow coordinates four crews. Only the initial analysis stage changes; the Debate and Memo Writer crews remain the same.

| Order | Crew | Process | Output |
| --- | --- | --- | --- |
| 1 | Profiling | Hierarchical: manager agent and Company Profiler | Company profile, including missing information |
| 2 | Analysis | Sequential process; three asynchronous specialist tasks followed by a synchronous aggregation task | Consolidated detailed analysis |
| 3 | Debate | Sequential: Formatter, Pro Extractor, Contra Extractor, Judge | Debate findings and judgment |
| 4 | Memo Writer | One agent, one task | Formatted final memo |

### Flow Diagram — Version 2

The Flow runs Profiling before Analysis. Specialist tasks receive the general profile plus their relevant specialist information; the synchronous aggregator waits for all three results.

```mermaid
flowchart TD
    Input["User input"] --> Manager
    subgraph Profiling["Profiling Crew — hierarchical"]
        Manager["Manager agent — quality review"]
        Profiler["Company Profiler — retrieval tools"]
        Manager -->|"Delegate / bounded retry"| Profiler
        Profiler -->|"Profile and information gaps"| Manager
    end
    Manager -->|"Accept profile or record remaining gaps"| Profile["Company profile"]
    subgraph Analysis["Analysis Crew — sequential process"]
        Tech["Tech task — async"]
        Commercial["Commercial task — async"]
        Team["Team task — async"]
        Aggregate["Memo Writer agent — synchronous aggregation"]
        Tech --> Aggregate
        Commercial --> Aggregate
        Team --> Aggregate
    end
    Profile -->|"General + tech context"| Tech
    Profile -->|"General + commercial context"| Commercial
    Profile -->|"General + team context"| Team
    Profile -->|"Profile input"| Aggregate
    Aggregate --> Report["Consolidated analysis report"]
    Report --> Review{"Human review in Flow"}
    Review -->|"Export analysis"| AnalysisOut["Analysis-only deliverable"]
    Review -->|"Skip Debate"| Writer["Final Memo Writer Crew"]
    Review -->|"Run Debate"| Debate["Debate Crew — sequential"]
    Debate --> Writer
    Writer --> Memo["Formatted memo"]
```

Profiling retries are bounded by the configured maximum iterations and guided by prompt instructions against repeated requests for the same missing information. The Analysis Crew's aggregation task and the final Memo Writer Crew are separate execution stages. Debate retains the same four-agent sequence as Version 1.

Both flow diagrams show the implemented human review. The proposed automated eligibility check is described above.

### Profiling Crew

The manager acts as the quality guarantor for the profile. The Profiler uses search and other retrieval tools to gather company information. When information is missing, the manager may delegate another retrieval iteration within configured limits.

The implementation combines a hardcoded maximum iteration count with prompt instructions not to repeatedly request the same unavailable information. Remaining gaps are recorded as missing information. The prompt instruction guides behavior; the configured iteration limit bounds execution.

### Analysis Crew

Tech, Commercial and Team tasks use asynchronous execution and run in parallel. Each receives the general company profile plus the portion relevant to its specialty. Unrelated specialist information is excluded to reduce irrelevant context, distraction and unnecessary agentic loops.

A Memo Writer agent then performs a synchronous aggregation task. It waits for all three specialist tasks and combines their analyses with the company profile into a detailed intermediate analysis.

This aggregation task is distinct from final memo generation, which occurs in the separate Memo Writer Crew after Debate or directly after human review when Debate is skipped.

### Version Comparison

| Aspect | Version 1 | Version 2 |
| --- | --- | --- |
| Crew count | Three | Four |
| Profiling | Inside the hierarchical Analysis Crew | Separate hierarchical crew |
| Supervisor role | Coordinates analysis and delegation | Guarantees profiling quality |
| Specialist execution | Hierarchical orchestration combined with asynchronous tasks; overlapping delegations observed | Explicit asynchronous tasks in a sequential process, followed by synchronous aggregation |
| Context transfer | Manager selects and reformulates delegated context | General profile plus explicitly selected specialist context |
| Debate and final memo | Shared downstream design | Same as Version 1 |

Version 2 changes orchestration to address the observed issues; improvement must still be evaluated through testing. The necessity of a supervisor remains an [open question](due_diligence_open_points.md#op-03--is-supervisor-orchestration-necessary).

## LangGraph

A single graph orchestrates the workflow and reuses the shared agent classes through the LangGraph adapter. The Supervisor is a project-defined node with an explicit router. The application defines the routing rules and target nodes in code. Routing uses those rules and the user's resume decision. The workflow uses neither `create_supervisor` nor LLM-driven selection of the next agent.

| Node or component | Responsibility |
| --- | --- |
| Request Handler | Requests the target company information from the user. The graph skips this node when it already has the required input, as with a complete REST request. |
| Supervisor and router | The router first calls the Profiler. After each pass, the Supervisor reviews the profile and returns missing information and feedback on how to improve the research. The router proceeds to Fan-out when the profile is complete or after three passes in total, including the initial pass. |
| Profiler | Produces the company profile and uses the Supervisor's feedback on subsequent passes. |
| Fan-out | Uses `Send` to run the Tech, Commercial and Team analyst nodes in parallel. |
| Aggregator | Waits for all three specialist analyses. An LLM consolidates them and the company profile into a single analysis. Control then returns to the Supervisor. |
| Supervisor review and interrupt | The same Supervisor assesses the completeness of the consolidated analysis and returns a score from 1 to 10 and a review summary. Its router triggers an interrupt. The graph pauses while the user reviews and validates the analysis and chooses how to continue. |
| Memo Writer | Formats the available analysis and findings according to the memo specifications. Both resume paths converge here. |

### Resume after Human Review

| Resume value | Route |
| --- | --- |
| `end` | Go directly to Memo Writer and format the consolidated analysis as the final memo. |
| `proceed` | Run Debate using the [previously documented sequence](#debate-crew--shared-by-both-versions), then pass the findings to Memo Writer. The initial Debate formatting step runs when enabled. |

The score informs human review. The user's resume value selects the route. The SQLite checkpointer allows the graph to resume using the same `thread_id`, including after an application restart when the saved database is available. See [LangGraph Persistence and Resume](due_diligence_runtime.md#langgraph-persistence-and-resume).

### Flow Diagram — Profiling and Analysis

```mermaid
flowchart TD
    Start["Start"] --> InputReady{"Required input available?"}
    InputReady -->|"Yes"| Router["Supervisor router"]
    InputReady -->|"No"| Handler["Request Handler"]
    Handler --> Router
    Router -->|"Initial pass or refinement"| Profiler["Profiler"]
    Profiler -->|"Company profile"| Supervisor["Supervisor profile review"]
    Supervisor -->|"Information gaps and research feedback"| Router
    Router -->|"Complete profile or 3 passes reached"| FanOut["Fan-out via Send"]
    FanOut --> Tech["Tech analysis"]
    FanOut --> Commercial["Commercial analysis"]
    FanOut --> Team["Team analysis"]
    Tech --> Aggregator["Aggregator"]
    Commercial --> Aggregator
    Team --> Aggregator
```

### Flow Diagram — Review and Memo

```mermaid
flowchart TD
    Aggregator["Aggregator"] --> Supervisor["Supervisor completeness review"]
    Supervisor -->|"Score and review summary"| Router["Supervisor router"]
    Router --> Interrupt["Interrupt for human review"]
    Interrupt --> Resume{"User resumes graph"}
    Resume -->|"end"| Writer["Memo Writer"]
    Resume -->|"proceed"| Debate["Debate"]
    Debate --> Writer
    Writer --> Memo["Formatted memo"]
```
