# Startup Due Diligence MAS — MCP Server

## Purpose

A task manager MCP server lets the analysis reviewer create follow-up tasks for gaps found in the analysis. Each task goes to the team member whose role matches the topic.

## Server

| Item | Value |
| --- | --- |
| Code | `src/due_diligence_mas/mcp/task_manager.py` (FastMCP) |
| Start | `poetry run task-server` |
| Transport | `stdio` by default; `streamable-http` with `MCP_TRANSPORT`, `MCP_HOST` (default `127.0.0.1`), `MCP_PORT` (default `8200`) |
| Inspect | `poetry run mcp dev src/due_diligence_mas/mcp/task_manager.py` (needs Node.js) |

With `stdio` the client spawns the server as a subprocess.

## Tools

| Tool | Input | Output |
| --- | --- | --- |
| `get_users` | none | List of users (`id`, `name`, `role`: `tech` or `commercial`). Users are mocked with fixed ids. |
| `create_task` | `assignee` (user UUID), `description`, `priority` (`HIGH`, `MEDIUM`, `LOW`) | The created task. It is saved as `<task_id>.json` in `src/due_diligence_mas/mcp/tasks/`. |

## Usage in the Workflow

The Analysis Reviewer agent (CrewAI Version 2) uses the tools through the `mcp_tasks` tool key, which starts the server over `stdio`. It decides autonomously whether to create tasks:

- call `get_users` first and assign by role;
- at most one task per topic (tech, commercial), so at most two in total;
- priority is the highest among the grouped items;
- no tasks when the analysis is complete.

LangGraph does not use the MCP server yet.
