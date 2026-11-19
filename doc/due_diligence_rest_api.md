# Startup Due Diligence MAS — REST API

Updated 2026-11-19

Related documents · [Architecture](due_diligence_architecture.md) · [State, persistence and observability](due_diligence_runtime.md)

## Servers

Two REST servers expose the due diligence workflow. They share request and response models and the same service operations.

| Framework | Port | Workflow instance |
| --- | --- | --- |
| LangGraph | 8000 | The server initializes the graph at startup and reuses it across executions. A separate checkpoint thread holds each execution's state. |
| CrewAI | 8100 | The server creates a new Flow for each inference. |

Both servers write their own logs to files.

## Service Operations

The client tracks progress by polling Get Status. The service names below describe the operations.

| Operation | Client input | Server behavior |
| --- | --- | --- |
| Run | Company name, website and additional information | Generates a session ID before launching the workflow. Kicks off the CrewAI Flow or runs the LangGraph graph in a background thread, then responds immediately with the session ID in a cookie. In LangGraph, the runner receives this ID as the checkpoint `thread_id`. A complete REST request lets the graph skip the interactive Request Handler. |
| Get Status | Session ID from the cookie | Reads the execution record and returns the current status and execution information. When the system is waiting for a human response, it also returns the analysis preview. |
| Resume | Execution identifier and a decision of `proceed` or `end` | Resumes the selected execution. The LangGraph runner receives the original `thread_id` and the decision. With `proceed`, Debate runs before the Memo Writer. With `end`, the workflow goes directly to the Memo Writer. |
| Get Memo | Execution identifier | Returns the final memo as Markdown text. |

For LangGraph, Get Status reads from the SQLite execution table. The checkpointer uses the same `thread_id` to restore graph state for Resume. Persistent execution support for CrewAI is pending.

## MCP Server

Status · To do.
