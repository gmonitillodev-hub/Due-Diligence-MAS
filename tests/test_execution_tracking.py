import json
import operator
from typing import Annotated, TypedDict

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.utils.execution_store import save_execution
from due_diligence_mas.mas_definition.utils.usage_tracker import UsageTracker


def _usage_messages():
    while True:
        yield AIMessage(content="x", usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15})


def test_tracker_counts_calls_of_parallel_nodes_without_explicit_config():
    llm = GenericFakeChatModel(messages=_usage_messages())

    class State(TypedDict):
        out: Annotated[list, operator.add]

    def worker(state):
        llm.invoke("hi")
        return {"out": ["w"]}

    builder = StateGraph(State)
    builder.add_node("worker", worker)
    builder.add_conditional_edges(START, lambda s: [Send("worker", s)] * 3, ["worker"])
    builder.add_edge("worker", END)

    tracker = UsageTracker()
    with tracker.measure():
        builder.compile().invoke({"out": []}, config={"callbacks": [tracker]})

    metrics = tracker.metrics()
    assert metrics["llm_calls"] == 3
    assert metrics["tokens"] == {"prompt": 30, "completion": 15, "total": 45}
    assert len(metrics["tracing"]["root_run_ids"]) == 1


def test_tracker_restore_continues_from_snapshot():
    tracker = UsageTracker()
    tracker.calls, tracker.prompt_tokens = 2, 7
    restored = UsageTracker.restore(tracker.snapshot())
    assert restored.snapshot() == tracker.snapshot()


def test_save_execution_writes_memo_as_is_and_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("EXECUTIONS_DIR", str(tmp_path))
    memo = "# Memo\n\n| a | b |\n"

    folder = save_execution("Acme Inc.", Framework.LANG_GRAPH, memo, {"llm_calls": 1})

    assert (folder / "memo.md").read_text(encoding="utf-8") == memo
    data = json.loads((folder / "metrics.json").read_text(encoding="utf-8"))
    assert data == {"company": "Acme Inc.", "framework": "langgraph", "llm_calls": 1}
    assert folder.name.startswith("Acme_Inc_langgraph_")
