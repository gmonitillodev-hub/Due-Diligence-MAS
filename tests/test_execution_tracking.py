import operator
from typing import Annotated, TypedDict

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

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
