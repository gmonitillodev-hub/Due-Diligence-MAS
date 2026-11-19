"""
Local SQLite db of the executions (same file also holds the LangGraph checkpoints).

Tables:
    executions: one row per execution (thread), updated while the graph runs.
    trackers:   usage totals (LLM calls, tokens, time) kept while an execution waits for the human review.
"""
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

# <repo>/doc/executions/executions.db, overridable with EXECUTIONS_DB
DEFAULT_EXECUTIONS_DB = Path(__file__).resolve().parents[4] / "doc" / "executions" / "executions.db"


class ExecutionStatus(str, Enum):
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"  # paused at the human review, resume with Proceed / End
    COMPLETED = "completed"
    FAILED = "failed"


EXECUTIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS executions (
    thread_id         TEXT PRIMARY KEY,  -- session id, same as the LangGraph thread id
    company_name      TEXT,
    framework         TEXT NOT NULL,     -- langgraph / crewai
    status            TEXT NOT NULL,     -- ExecutionStatus
    current_node      TEXT,              -- last node finished (human_review while paused), NULL when completed
    current_crew      TEXT,              -- CrewAI only, NULL for LangGraph
    metrics           TEXT,              -- JSON: time, LLM calls, tokens, tracing
    memo_markdown     TEXT,              -- final memo
    memo_file_path    TEXT,              -- memo.md saved in the execution folder
    pending_review    TEXT,              -- JSON: analysis preview and options shown to the human while paused
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
)
"""

TRACKERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS trackers (
    thread_id TEXT PRIMARY KEY,
    snapshot  TEXT NOT NULL              -- JSON from UsageTracker.snapshot()
)
"""

# Columns holding JSON: dicts are dumped on write and parsed on read
JSON_COLUMNS = ("metrics", "pending_review")
UPDATABLE_COLUMNS = {
    "company_name", "status", "current_node", "current_crew", "metrics", "memo_markdown", "memo_file_path", "pending_review",
}

# Columns and status values of the first version of the table
LEGACY_COLUMNS = {"company": "company_name", "memo": "memo_markdown", "memo_path": "memo_file_path", "interrupt": "pending_review"}


def db_path() -> Path:
    path = Path(os.getenv("EXECUTIONS_DB") or DEFAULT_EXECUTIONS_DB)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    connection.execute(EXECUTIONS_SCHEMA)
    connection.execute(TRACKERS_SCHEMA)
    _migrate_legacy_columns(connection)
    return connection


def _migrate_legacy_columns(connection: sqlite3.Connection) -> None:
    existing = {row["name"] for row in connection.execute("PRAGMA table_info(executions)")}
    for old, new in LEGACY_COLUMNS.items():
        if old in existing:
            connection.execute(f"ALTER TABLE executions RENAME COLUMN {old} TO {new}")
    if "pending_review" not in existing and "interrupt" not in existing:
        connection.execute("ALTER TABLE executions ADD COLUMN pending_review TEXT")
    connection.execute("UPDATE executions SET status = 'awaiting_review' WHERE status = 'interrupted'")
    connection.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def create_execution(thread_id: str, framework: str, company_name: Optional[str] = None) -> None:
    """Insert the execution as running; a thread that already exists is restarted."""
    now = _now()
    with closing(_connect()) as connection, connection:
        connection.execute(
            "INSERT OR REPLACE INTO executions (thread_id, company_name, framework, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (thread_id, company_name, framework, ExecutionStatus.RUNNING.value, now, now),
        )


def update_execution(thread_id: str, **fields) -> None:
    """Update the given columns (dicts are stored as JSON, `status` can be an ExecutionStatus) and refresh `updated_at`."""
    unknown = set(fields) - UPDATABLE_COLUMNS
    if unknown:
        raise ValueError(f"Unknown execution columns: {sorted(unknown)}")

    for column in JSON_COLUMNS:
        if isinstance(fields.get(column), dict):
            fields[column] = json.dumps(fields[column], ensure_ascii=False)
    if isinstance(fields.get("status"), ExecutionStatus):
        fields["status"] = fields["status"].value

    assignments = ", ".join(f"{column} = ?" for column in [*fields, "updated_at"])
    with closing(_connect()) as connection, connection:
        connection.execute(
            f"UPDATE executions SET {assignments} WHERE thread_id = ?", (*fields.values(), _now(), thread_id)
        )


def get_execution(thread_id: str) -> Optional[dict]:
    """Return the execution row (JSON columns parsed) or None if the thread does not exist."""
    with closing(_connect()) as connection:
        row = connection.execute("SELECT * FROM executions WHERE thread_id = ?", (thread_id,)).fetchone()
    if row is None:
        return None

    execution = dict(row)
    for column in JSON_COLUMNS:
        if execution[column]:
            execution[column] = json.loads(execution[column])
    return execution


def save_tracker(thread_id: str, snapshot: dict) -> None:
    """Store the usage totals of an execution, so they survive between run() and resume()."""
    with closing(_connect()) as connection, connection:
        connection.execute(
            "INSERT OR REPLACE INTO trackers (thread_id, snapshot) VALUES (?, ?)", (thread_id, json.dumps(snapshot))
        )


def load_tracker(thread_id: str) -> Optional[dict]:
    with closing(_connect()) as connection:
        row = connection.execute("SELECT snapshot FROM trackers WHERE thread_id = ?", (thread_id,)).fetchone()
    return json.loads(row["snapshot"]) if row else None


def delete_tracker(thread_id: str) -> None:
    with closing(_connect()) as connection, connection:
        connection.execute("DELETE FROM trackers WHERE thread_id = ?", (thread_id,))
