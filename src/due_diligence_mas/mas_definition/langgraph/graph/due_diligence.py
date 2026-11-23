import sqlite3
import uuid
from due_diligence_mas.mas_definition.classes import company as company_classes
from due_diligence_mas.mas_definition.classes.company import CompanyInfo
from due_diligence_mas.mas_definition.langgraph.classes import shared_state
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.langgraph import (
    ANALYSIS_AGGREGATOR_NODE, ANALYST_AGENTS, DEBATE_FORMATTER_NODE, DEBATE_JUDGE_NODE, ENABLED_ANALYST_AGENTS, FAN_OUT_NODE, HUMAN_REVIEW_NODE,
    MEMO_WRITER_NODE, OPPORTUNITY_ANALYST_NODE, PROFILER_NODE, REQUEST_HANDLER_NODE, RISK_ANALYST_NODE, SUPERVISOR_NODE, skip_debate_formatter,
)
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State
from due_diligence_mas.mas_definition.langgraph.node.analysts import analyst_fan_out_node, commercial_analyst_node, team_analyst_node, tech_reviewer_node
from due_diligence_mas.mas_definition.langgraph.node.debate import debate_formatter_node, debate_judge_node, opportunity_analyst_node, risk_analyst_node
from due_diligence_mas.mas_definition.langgraph.node.profiler import company_profiler_node
from due_diligence_mas.mas_definition.langgraph.node.supervisor import debate_entry_node, supervisor_node, supervisor_router
from due_diligence_mas.mas_definition.langgraph.node.human_in_the_loop import human_review_node, preview_and_confirm_router
from due_diligence_mas.mas_definition.langgraph.node.request_handler import request_handler_node
from due_diligence_mas.mas_definition.langgraph.node.writer import analysis_aggregator_node, memo_writer_node
from due_diligence_mas.mas_definition.utils.agent_names import get_agent_node_name as node_name
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from dotenv import load_dotenv
from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.utils.execution_db import (
    ExecutionStatus, create_execution, db_path, delete_tracker, get_execution, load_tracker, save_tracker, update_execution,
)
from due_diligence_mas.mas_definition.utils.usage_tracker import UsageTracker
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel


AGENT_NODES = {
    AgentName.TECH_REVIEWER: tech_reviewer_node,
    AgentName.COMMERCIAL_ANALYST: commercial_analyst_node,
    AgentName.TEAM_ANALYST: team_analyst_node,
    AgentName.DEBATE_FORMATTER: debate_formatter_node,
    AgentName.OPPORTUNITY_ANALYST: opportunity_analyst_node,
    AgentName.RISK_ANALYST: risk_analyst_node,
    AgentName.DEBATE_JUDGE: debate_judge_node,
}


def _pydantic_models(*modules) -> list[tuple[str, str]]:
    """(module, class) of the pydantic models defined in the modules: the types allowed in the checkpoints."""
    return [
        (module.__name__, name)
        for module in modules
        for name, cls in vars(module).items()
        if isinstance(cls, type) and issubclass(cls, BaseModel) and cls.__module__ == module.__name__
    ]


STATE_MODELS = _pydantic_models(company_classes, shared_state)


class DueDiligence_Graph():
    
    def __init__(self):
        
        load_dotenv()
        
        self.graph_builder = StateGraph(DueDiligence_State)
        
        self._build_nodes()
        self._build_edges()
        self._compile_grap()
        
    def _build_nodes(self):
        
        self.graph_builder.add_node(REQUEST_HANDLER_NODE, request_handler_node)
        self.graph_builder.add_node(PROFILER_NODE, company_profiler_node)
        self.graph_builder.add_node(SUPERVISOR_NODE, supervisor_node)
        self.graph_builder.add_node(HUMAN_REVIEW_NODE, human_review_node)
        self.graph_builder.add_node(FAN_OUT_NODE, lambda state: {})
        self.graph_builder.add_node(ANALYSIS_AGGREGATOR_NODE, analysis_aggregator_node)
        
        self.graph_builder.add_node(MEMO_WRITER_NODE, memo_writer_node)

        for agent, function in AGENT_NODES.items():
            if agent == AgentName.DEBATE_FORMATTER and skip_debate_formatter():
                continue
            self.graph_builder.add_node(node_name(agent), function)

    def _build_edges(self):
        """Wire the graph: profiler <-> supervisor loop, human review, analyst fan-out/join, optional debate (formatter, PRO, CONTRO, judge) and memo writer."""
        self.graph_builder.add_edge(START, REQUEST_HANDLER_NODE)
        self.graph_builder.add_edge(REQUEST_HANDLER_NODE, PROFILER_NODE)
        self.graph_builder.add_edge(PROFILER_NODE, SUPERVISOR_NODE)

        self.graph_builder.add_conditional_edges(SUPERVISOR_NODE, supervisor_router, [PROFILER_NODE, FAN_OUT_NODE, HUMAN_REVIEW_NODE])
        self.graph_builder.add_conditional_edges(HUMAN_REVIEW_NODE, preview_and_confirm_router, [debate_entry_node(), MEMO_WRITER_NODE])
        self.graph_builder.add_conditional_edges(FAN_OUT_NODE, analyst_fan_out_node, [node_name(a) for a in ANALYST_AGENTS])

        self.graph_builder.add_edge([node_name(a) for a in ENABLED_ANALYST_AGENTS], ANALYSIS_AGGREGATOR_NODE)
        self.graph_builder.add_edge(ANALYSIS_AGGREGATOR_NODE, SUPERVISOR_NODE)
        
        if not skip_debate_formatter():
            self.graph_builder.add_edge(DEBATE_FORMATTER_NODE, OPPORTUNITY_ANALYST_NODE)
        self.graph_builder.add_edge(OPPORTUNITY_ANALYST_NODE, RISK_ANALYST_NODE)
        self.graph_builder.add_edge(RISK_ANALYST_NODE, DEBATE_JUDGE_NODE)
        self.graph_builder.add_edge(DEBATE_JUDGE_NODE, MEMO_WRITER_NODE)
        
        self.graph_builder.add_edge(MEMO_WRITER_NODE, END)

        
    def _compile_grap(self):
        """Compile the graph. State checkpoints share the executions db, so a paused execution survives a restart."""
        serializer = JsonPlusSerializer(allowed_msgpack_modules=STATE_MODELS)
        checkpointer = SqliteSaver(sqlite3.connect(db_path(), check_same_thread=False), serde=serializer)

        self.compiled_graph = self.graph_builder.compile(checkpointer=checkpointer)

    def run(self, company_info: CompanyInfo = None, thread_id: str = None) -> dict:
        """Start the graph: it runs until the human review (interrupt) or the end."""
        if thread_id and self._check_status(thread_id) is not None:
            raise ValueError("Ongoing or completed execution.")
        create_execution(thread_id, Framework.LANG_GRAPH.value, company_info.company_name if company_info else None)

        return self._execute(DueDiligence_State(company_info=company_info), thread_id, UsageTracker())

    def resume(self, decision, thread_id: str) -> dict:       
        """Resume the graph after the human review with the decision (Proceed / End)."""
        
        if self._check_status(thread_id, ExecutionStatus.AWAITING_REVIEW.value) == False:
            raise ValueError("The execution is not interrupted")
        
        snapshot = load_tracker(thread_id)
        tracker = UsageTracker.restore(snapshot) if snapshot else UsageTracker()
        update_execution(thread_id, status=ExecutionStatus.RUNNING, pending_review=None)

        return self._execute(Command(resume=decision), thread_id, tracker)

    def _execute(self, graph_input, thread_id: str, tracker: UsageTracker) -> dict:
        """Stream the graph keeping the execution row up to date, then close it as awaiting review or completed. The human wait between run() and resume() is outside measure(), so it is not counted."""
        config = {"configurable": {"thread_id": thread_id}, "callbacks": [tracker]}
        interrupt_payload = None

        try:
            with tracker.measure():
                for chunk in self.compiled_graph.stream(graph_input, config, stream_mode="updates"):
                    for node, update in chunk.items():
                        if node == "__interrupt__":
                            interrupt_payload = update[0].value
                        else:
                            update_execution(thread_id, current_node=node)

            state = self.compiled_graph.get_state(config).values
            company = state["company_info"].company_name if state.get("company_info") else None

            if interrupt_payload is not None:
                return self._pause(thread_id, tracker, company, interrupt_payload)
            return self._complete(thread_id, tracker, company, state.get("final_report"))
        except Exception:
            update_execution(thread_id, status=ExecutionStatus.FAILED, metrics=tracker.metrics())
            raise

    def _pause(self, thread_id: str, tracker: UsageTracker, company: str, interrupt_payload: dict) -> dict:
        """Waiting for the human review: keep the usage totals for the resume."""
        save_tracker(thread_id, tracker.snapshot())
        update_execution(
            thread_id, 
            status=ExecutionStatus.AWAITING_REVIEW, 
            current_node=HUMAN_REVIEW_NODE, 
            company_name=company,
            metrics=tracker.metrics(), 
            pending_review=interrupt_payload,
        )
        return {"sessionId": thread_id, "status": ExecutionStatus.AWAITING_REVIEW.value, "pending_review": interrupt_payload}

    def _complete(self, thread_id: str, tracker: UsageTracker, company: str, final_report: str) -> dict:
        """Store the memo and the metrics in the db row."""
        fields = {"status": ExecutionStatus.COMPLETED, "current_node": None, "company_name": company, "metrics": tracker.metrics()}
        outcome = {"sessionId": thread_id, "status": ExecutionStatus.COMPLETED.value, "final_report": final_report}
        if final_report:
            fields["memo_markdown"] = final_report

        update_execution(thread_id, **fields)
        delete_tracker(thread_id)
        return outcome

    @staticmethod
    def _check_status(thread_id: str, expected_status: str = None) -> bool | None:
        """ 
            Check existance and status of an execution
            
            Returns:
                None if the execution doesn't exists
                True if the status is correct
                False if the status is wrong
        """
        execution = get_execution(thread_id)
        if execution is None:
            return None
        else:
            return True if execution["status"] == expected_status else False

def main():
    thread_id = str(uuid.uuid4())
    graph = DueDiligence_Graph()
    outcome = graph.run(thread_id=thread_id)
    while outcome["status"] == ExecutionStatus.AWAITING_REVIEW.value:
        outcome = graph.resume(input("Proceed / End > "), thread_id)


if __name__ == "__main__":
    main()
