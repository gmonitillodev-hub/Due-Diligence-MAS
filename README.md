# Due Diligence MAS

Multi-agent system that produces a startup due diligence memo. It implements the same workflow in two frameworks, **CrewAI** and **LangGraph**, to compare them.

**Input:** startup name, website, sector, additional info → **Output:** a Markdown memo with profile, specialist analyses and, optionally, debate findings.

## Overview

1. **Profiling** — company profile and information gaps.
2. **Analysis** — Tech, Commercial and Team specialists run in parallel, then one aggregation.
3. **Analysis review** — a reviewer scores the analysis (0–10) and may create follow-up tasks through an MCP server.
4. **Human review** — the user chooses `proceed` (run Debate) or `end` (skip it).
5. **Debate** (optional) — Pro vs. Contra extractors, judged.
6. **Memo** — final formatted memo.

| Aspect | Choice |
| --- | --- |
| Orchestration patterns | Debate/adversarial, Supervisor, Sequential |
| Agentic paradigms | ReAct; Reflexion (LangGraph Supervisor) |
| CrewAI | Version 2 under test; Version 1 discarded ([open points](doc/open_points.md)) |
| Persistence | LangGraph: SQLite; CrewAI: to do |

## Setup

Requires Python 3.12–3.13 and [Poetry](https://python-poetry.org/).

```bash
poetry install
cp .env.example .env   # set LLM provider and tool API keys
```

## Run

```bash
poetry run crewai-server     # CrewAI REST server, http://127.0.0.1:8100
poetry run langgraph-server  # LangGraph REST server, http://127.0.0.1:8000
poetry run task-server       # Task manager MCP server (stdio)
```

CrewAI flow from the terminal (prompts for company details, then asks for approval before the debate):

```bash
poetry run python -m due_diligence_mas.mas_definition.crewai_fr.flows.due_diligence
```

Operations and MCP details: [REST API](doc/rest_api.md), [MCP Server](doc/mcp_task_server.md).

## Layout

| Path | Content |
| --- | --- |
| `src/due_diligence_mas/mas_definition/agents` | Shared agent classes and framework adapters |
| `src/due_diligence_mas/mas_definition/constants` | Agent, tool and review definitions |
| `src/due_diligence_mas/mas_definition/classes` | Shared models (`CompanyInfo`, `CompanyProfile`, `ProfiledCompany`, `AnalysisReview`) |
| `src/due_diligence_mas/mas_definition/crewai_fr` | CrewAI flow and crews |
| `src/due_diligence_mas/mas_definition/langgraph` | LangGraph graph and nodes |
| `src/due_diligence_mas/mas_definition/tools` | Search, LinkedIn, GitHub and MCP tools |
| `src/due_diligence_mas/api_gateway` | REST servers |
| `src/due_diligence_mas/mcp` | Task manager MCP server |

## Docs

- [Architecture](doc/architecture.md)
- [Open points](doc/open_points.md)
- [State, persistence and observability](doc/runtime.md)
- [REST API](doc/rest_api.md)
- [MCP Server](doc/mcp_task_server.md)
- [Benchmark registry](doc/benchmark_registry.md)
