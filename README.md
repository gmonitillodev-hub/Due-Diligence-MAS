# Due Diligence MAS

Multi-agent system that produces a startup due diligence memo. It compares CrewAI and LangGraph; the CrewAI implementation lives in `src/due_diligence_mas/crewai_fr`.

**Input:** startup name, website, sector, additional info → **Output:** a Markdown memo with profile, specialist analyses and debate findings.

## Flow

Profiling → specialist analysis (tech, commercial, team) → human approval → debate (risk vs. opportunity) → memo.

## Setup

Requires Python 3.12–3.13 and [Poetry](https://python-poetry.org/).

```bash
poetry install
cp .env.example .env   # set LLM provider and tool API keys
```

## Run

```bash
poetry run due-diligence
```

The flow prompts for the company details, then asks for approval before the debate phase.

## Layout

| Path | Content |
| --- | --- |
| `src/due_diligence_mas/classes` | Shared typed models (`CompanyInfo`, `CompanyProfile`, `ProfiledCompany`) |
| `src/due_diligence_mas/crewai_fr` | Flow, crews, agents, tools |
| `src/due_diligence_mas/constants` | Agent and tool definitions |
| `src/due_diligence_mas/providers` | LLM provider |

## Docs

- [Overview](doc/due_diligence_overview.md)
- [Architecture](doc/due_diligence_architecture.md)
- [Open points](doc/due_diligence_open_points%20(1).md)
- [Benchmark registry](doc/due_diligence_benchmark_registry.md)
