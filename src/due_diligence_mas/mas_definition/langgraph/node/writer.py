import time

from due_diligence_mas.mas_definition.agents.writer.memo_writer import MemoWriter_Agent
from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.constants.langgraph import ANALYSIS_AGGREGATOR_NODE, MEMO_WRITER_NODE
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State
from due_diligence_mas.mas_definition.langgraph.node.node_log import log_node as _log


def _run_writer_agent(node: str, task: str, topic: str) -> str:
    """Build the memo writer for the given task ("aggregation" or "memo") and return its output."""
    _log(node, "start", task=task, topic_chars=len(topic))
    t0 = time.perf_counter()

    writer = MemoWriter_Agent(framework=Framework.LANG_GRAPH, task=task)
    writer.build_tasks(topic, key=task)

    agent = writer.get_agent()
    _log(node, "agent built", tools=list(writer.tools))

    result = agent.invoke(
                {
                    "messages": writer.get_tasks()
                },
                #config=self.checkpointer_config,
                #context=session_data,
            )
    output = result["messages"][-1].content

    _log(node, "end", elapsed_s=round(time.perf_counter() - t0, 2))
    return output


def analysis_aggregator_node(state: DueDiligence_State):
    """Consolidate the specialists' reports into a single analysis."""
    profile = state.company_profile
    reports = {
        "TECHNOLOGY": profile.tech if profile else None,
        "COMMERCIAL": profile.commercial if profile else None,
        "TEAM": profile.team if profile else None,
    }
    topic = "\n\n".join(f"{name} REPORT:\n" + "\n".join(entries or ["Not available"]) for name, entries in reports.items())

    return {"analysis_results": _run_writer_agent(ANALYSIS_AGGREGATOR_NODE, "aggregation", topic)}


def memo_writer_node(state: DueDiligence_State):
    """Write the final memo from the analysis and the debate (if performed)."""
    topic = (
        f"ANALYSIS:\n{state.analysis_results}\n\n"
        f"DEBATE:\n{state.debate_results or 'Debate not performed'}"
    )
    
    final_report =_run_writer_agent(MEMO_WRITER_NODE, "memo", topic)

    return {"final_report": final_report}
