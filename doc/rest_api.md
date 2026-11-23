# Startup Due Diligence MAS — REST API

Updated 2026-11-23

Related documents: [Architecture](architecture.md) · [State, persistence and observability](runtime.md)

## Servers

Two REST servers expose the workflow with the same models and service operations.

| Framework | Port | Workflow instance |
| --- | --- | --- |
| LangGraph | 8000 | Graph created at startup and reused; each execution has its own checkpoint thread. |
| CrewAI | 8100 | New Flow for each inference. |

Both servers write logs to files.

## Service Operations

The client polls Get Status to follow progress.

| Operation | Client input | Server behavior |
| --- | --- | --- |
| Run | Company name, website and additional information | Generates a session ID, starts the workflow in the background and returns the ID in a cookie. In LangGraph the ID is the `thread_id`; a complete request skips the Request Handler. |
| Get Status | Session ID (cookie) | Returns status and execution information. While waiting for human review it also returns the analysis preview and the review score. |
| Resume | Execution ID and decision `proceed` or `end` | `proceed` runs Debate, then Memo Writer; `end` goes straight to Memo Writer. |
| Get Memo | Execution ID | Returns the final memo as Markdown. |

LangGraph reads status from the SQLite execution table and restores state with the same `thread_id`. Persistent execution support for CrewAI is pending.

## MCP Server

Status: implemented. See [MCP Server](mcp_task_server.md).
