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
from due_diligence_mas.mas_definition.utils.execution_store import save_execution
from due_diligence_mas.mas_definition.utils.usage_tracker import UsageTracker
from langgraph.checkpoint.memory import InMemorySaver


# Agent node functions, by agent
AGENT_NODES = {
    AgentName.TECH_REVIEWER: tech_reviewer_node,
    AgentName.COMMERCIAL_ANALYST: commercial_analyst_node,
    AgentName.TEAM_ANALYST: team_analyst_node,
    AgentName.DEBATE_FORMATTER: debate_formatter_node,
    AgentName.OPPORTUNITY_ANALYST: opportunity_analyst_node,
    AgentName.RISK_ANALYST: risk_analyst_node,
    AgentName.DEBATE_JUDGE: debate_judge_node,
}


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
        
        self.graph_builder.add_edge(START, REQUEST_HANDLER_NODE)
        self.graph_builder.add_edge(REQUEST_HANDLER_NODE, PROFILER_NODE)
        self.graph_builder.add_edge(PROFILER_NODE, SUPERVISOR_NODE)

        # Single supervisor: profile gate (back to the profiler or on to the fan out node), then completeness score of the aggregated analysis before the human review
        self.graph_builder.add_conditional_edges(SUPERVISOR_NODE, supervisor_router, [PROFILER_NODE, FAN_OUT_NODE, HUMAN_REVIEW_NODE])
        # Human in the loop: proceed with the debate or go straight to the memo writer
        self.graph_builder.add_conditional_edges(HUMAN_REVIEW_NODE, preview_and_confirm_router, [debate_entry_node(), MEMO_WRITER_NODE])
        self.graph_builder.add_conditional_edges(FAN_OUT_NODE, analyst_fan_out_node, [node_name(a) for a in ANALYST_AGENTS])

        # Join: the aggregator runs when all the dispatched analysts are done, then the supervisor scores its output
        self.graph_builder.add_edge([node_name(a) for a in ENABLED_ANALYST_AGENTS], ANALYSIS_AGGREGATOR_NODE)
        self.graph_builder.add_edge(ANALYSIS_AGGREGATOR_NODE, SUPERVISOR_NODE)
        
        # Debate: human review -> formatter (optional, SKIP_DEBATE_FORMATTER) -> PRO -> CONTRO -> judge
        
        if not skip_debate_formatter():
            self.graph_builder.add_edge(DEBATE_FORMATTER_NODE, OPPORTUNITY_ANALYST_NODE)
        self.graph_builder.add_edge(OPPORTUNITY_ANALYST_NODE, RISK_ANALYST_NODE)
        self.graph_builder.add_edge(RISK_ANALYST_NODE, DEBATE_JUDGE_NODE)
        self.graph_builder.add_edge(DEBATE_JUDGE_NODE, MEMO_WRITER_NODE)
        
        self.graph_builder.add_edge(MEMO_WRITER_NODE, END)

        
    def _compile_grap(self):
        
        checkpointer = InMemorySaver()

        self.compiled_graph = self.graph_builder.compile(checkpointer=checkpointer)

    def run(self, thread_id: str = "due-diligence") -> dict:
        """
        Run the graph to the end, resuming it after every human review, and store the execution
        (memo and metrics) in the executions folder.
        """
        tracker = UsageTracker()
        config = {"configurable": {"thread_id": thread_id}, "callbacks": [tracker]}

        with tracker.measure():
            result = self.compiled_graph.invoke(DueDiligence_State(), config)

        # The graph pauses at the human review: the wait is outside measure(), so it is not counted
        while "__interrupt__" in result:
            decision = input("Proceed / End > ")
            with tracker.measure():
                result = self.compiled_graph.invoke(Command(resume=decision), config)

        if result.get("final_report"):
            folder = save_execution(
                result["company_info"].company_name, Framework.LANG_GRAPH, result["final_report"], tracker.metrics()
            )
            print(f"\n Execution saved to: {folder}")

        return result


def main():
    DueDiligence_Graph().run()


if __name__ == "__main__":
    main()

