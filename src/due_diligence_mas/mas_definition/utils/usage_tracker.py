import os
import threading
import time
from contextlib import contextmanager
from typing import Any, Optional
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler

from due_diligence_mas.mas_definition.utils.llm_cost import summarize_cost


class UsageTracker(BaseCallbackHandler):
    """
    LangChain callback that totals LLM calls and tokens of a LangGraph run.

    Pass it once in the graph config (`config={"callbacks": [tracker]}`): LangGraph propagates it to every node,
    including parallel ones. It lives in memory, use `snapshot` / `restore` to carry the totals over a resume
    in another process.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.active_s = 0.0
        # Tokens by model, needed because every model has its own price
        self.models: dict[str, dict[str, int]] = {}
        self.root_run_ids: list[str] = []

    def on_chain_start(self, serialized: Any, inputs: Any, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        if parent_run_id is None:
            with self._lock:
                self.root_run_ids.append(str(run_id))

    def on_llm_end(self, response, **kwargs: Any) -> None:
        usage, model = {}, "unknown"
        try:
            message = response.generations[0][0].message
            usage = message.usage_metadata or {}
            model = message.response_metadata.get("model_name") or model
        except (IndexError, AttributeError):
            pass
        input_tokens, output_tokens = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        with self._lock:
            self.calls += 1
            self.prompt_tokens += input_tokens
            self.completion_tokens += output_tokens
            totals = self.models.setdefault(model, {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0})
            totals["calls"] += 1
            totals["prompt_tokens"] += input_tokens
            totals["completion_tokens"] += output_tokens

    @contextmanager
    def measure(self):
        """Add the elapsed time of the block to `active_s`; the human wait between two invokes stays out."""
        start = time.perf_counter()
        try:
            yield
        finally:
            with self._lock:
                self.active_s += time.perf_counter() - start

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "calls": self.calls,
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "active_s": self.active_s,
                "models": {model: dict(totals) for model, totals in self.models.items()},
                "root_run_ids": list(self.root_run_ids),
            }

    @classmethod
    def restore(cls, snapshot: dict) -> "UsageTracker":
        tracker = cls()
        tracker.calls = snapshot.get("calls", 0)
        tracker.prompt_tokens = snapshot.get("prompt_tokens", 0)
        tracker.completion_tokens = snapshot.get("completion_tokens", 0)
        tracker.active_s = snapshot.get("active_s", 0.0)
        tracker.models = {model: dict(totals) for model, totals in snapshot.get("models", {}).items()}
        tracker.root_run_ids = list(snapshot.get("root_run_ids", []))
        return tracker

    def metrics(self) -> dict:
        snap = self.snapshot()
        return {
            "total_time_s": round(snap["active_s"], 2),
            "llm_calls": snap["calls"],
            "tokens": {
                "prompt": snap["prompt_tokens"],
                "completion": snap["completion_tokens"],
                "total": snap["prompt_tokens"] + snap["completion_tokens"],
            },
            "cost_usd": summarize_cost(snap["models"]),
            "tracing": {
                "langsmith_enabled": os.getenv("LANGSMITH_TRACING", "").lower() == "true",
                "langsmith_project": os.getenv("LANGSMITH_PROJECT"),
                "root_run_ids": snap["root_run_ids"],
            },
        }
