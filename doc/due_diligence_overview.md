# Startup Due Diligence MAS — Overview

Status: working draft · Updated: 2026-11-15

Related documents: [Architecture](due_diligence_architecture.md) · [Open Points](due_diligence_open_points.md)

## Objective

Compare CrewAI and LangGraph to determine which framework best supports a multi-agent system (MAS) for startup due diligence and feasibility assessment.

Given a startup, the system gathers information, performs specialist analyses, evaluates supporting and opposing arguments, and produces a structured due diligence memo.

## Inputs and Output

| Item | Content |
| --- | --- |
| User inputs | Startup name, website, sector, additional information |
| Final output | A formatted memo combining company profiling, specialist analyses and debate findings |

## Requirements and Additional Features

| Category | Scope |
| --- | --- |
| Required | Parallel execution within the workflow |
| Required | Supervisor orchestration: a hierarchical process or at least one supervisor agent |
| Additional, implemented in CrewAI | Flow-based workflow coordination |
| Additional, implemented in CrewAI | Human-in-the-loop interaction; placement to be documented |

Agent responsibilities will be described in separate agent cards. This documentation focuses on architecture and implementation findings.

## Implementation Status

| Implementation | Status | Evaluation scope |
| --- | --- | --- |
| CrewAI — Version 1 | Implemented; under testing | Hierarchical analysis and parallel execution |
| CrewAI — Version 2 | Alternative implementation reported; architecture details pending in this draft | Comparison with Version 1 |
| LangGraph | To do | Comparison with CrewAI |

## Comparison Scope

Two comparisons are planned: CrewAI versus LangGraph, and Version 1 versus Version 2 within CrewAI.

The CrewAI variants change the initial analysis stage. The downstream Debate and Memo Writer crews remain unchanged.

No framework or CrewAI variant has been selected as the final solution. See [Architecture](due_diligence_architecture.md) for the current design and [Open Points](due_diligence_open_points.md) for findings and unresolved questions.
