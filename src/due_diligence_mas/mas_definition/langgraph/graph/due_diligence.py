from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.langgraph import ANALYSIS_AGGREGATOR_NODE, ANALYST_AGENTS, ENABLED_ANALYST_AGENTS, MEMO_WRITER_NODE
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State
from due_diligence_mas.mas_definition.langgraph.node.analysts import analyst_fan_out_node, commercial_analyst_node, team_analyst_node, tech_reviewer_node
from due_diligence_mas.mas_definition.langgraph.node.debate import debate_formatter_node, debate_judge_node, opportunity_analyst_node, risk_analyst_node
from due_diligence_mas.mas_definition.langgraph.node.profiler import company_profiler_node
from due_diligence_mas.mas_definition.langgraph.node.request_handler import request_handler_node
from due_diligence_mas.mas_definition.langgraph.node.writer import analysis_aggregator_node, memo_writer_node
from due_diligence_mas.mas_definition.utils.agent_names import get_agent_node_name as node_name
from langgraph.graph import StateGraph, START, END

REQUEST_HANDLER_NODE = "request_handler"
PROFILER_NODE = node_name(AgentName.COMPANY_PROFILER)

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
        
        self.graph_builder = StateGraph(DueDiligence_State)
        
        self._build_nodes()
        self._build_edges()
        self._compile_grap()
        
    def _build_nodes(self):
        
        self.graph_builder.add_node(REQUEST_HANDLER_NODE, request_handler_node)
        self.graph_builder.add_node(PROFILER_NODE, company_profiler_node)
        self.graph_builder.add_node(ANALYSIS_AGGREGATOR_NODE, analysis_aggregator_node)
        
        self.graph_builder.add_node(MEMO_WRITER_NODE, memo_writer_node)

        for agent, function in AGENT_NODES.items():
            self.graph_builder.add_node(node_name(agent), function)

    def _build_edges(self):
        
        self.graph_builder.add_edge(START, REQUEST_HANDLER_NODE)
        self.graph_builder.add_edge(REQUEST_HANDLER_NODE, PROFILER_NODE)
    
        # Fan-out: the router dispatches the analysts in parallel
        self.graph_builder.add_conditional_edges(PROFILER_NODE, analyst_fan_out_node, [node_name(a) for a in ANALYST_AGENTS])

        # Join: the aggregator runs when all the dispatched analysts are done
        for agent in ENABLED_ANALYST_AGENTS:
            self.graph_builder.add_edge(node_name(agent), ANALYSIS_AGGREGATOR_NODE)
        
        # Debate: aggregator -> formatter -> PRO -> CONTRO -> judge
        self.graph_builder.add_edge(ANALYSIS_AGGREGATOR_NODE, node_name(AgentName.DEBATE_FORMATTER))
        
        self.graph_builder.add_edge(node_name(AgentName.DEBATE_FORMATTER), node_name(AgentName.OPPORTUNITY_ANALYST))
        self.graph_builder.add_edge(node_name(AgentName.OPPORTUNITY_ANALYST), node_name(AgentName.RISK_ANALYST))
        self.graph_builder.add_edge(node_name(AgentName.RISK_ANALYST), node_name(AgentName.DEBATE_JUDGE))
        self.graph_builder.add_edge(node_name(AgentName.DEBATE_JUDGE), node_name(AgentName.MEMO_WRITER))
        
        self.graph_builder.add_edge(node_name(AgentName.MEMO_WRITER), END)

        
    def _compile_grap(self):
        
        self.compiled_graph = self.graph_builder.compile()
        

if __name__ == "__main__":
    
    graph = DueDiligence_Graph()
    print(graph)
    
    print(graph.compiled_graph.get_graph().draw_mermaid())
    
    state = DueDiligence_State()
    
    result = graph.compiled_graph.invoke(state)
    print(f"Res -> {result}")
