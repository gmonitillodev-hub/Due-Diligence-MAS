from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State
from due_diligence_mas.mas_definition.langgraph.node.analysts import analyst_fan_out_node, commercial_analyst_node, team_analyst_node, tech_reviewer_node
from due_diligence_mas.mas_definition.langgraph.node.profiler import company_profiler_node
from due_diligence_mas.mas_definition.langgraph.node.request_handler import request_handler_node
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.langgraph import ANALYSIS_AGGREGATOR_NODE, ANALYST_AGENTS, ENABLED_ANALYST_AGENTS
from due_diligence_mas.mas_definition.langgraph.node.writer import analysis_aggregator_node
from due_diligence_mas.mas_definition.utils.agent_names import get_agent_node_name
from langgraph.graph import StateGraph, START, END


class DueDiligence_Graph():
    
    def __init__(self):
        
        self.graph_builder = StateGraph(DueDiligence_State)
        
        self._build_nodes()
        self._build_edges()
        self._compile_grap()
        
    def _build_nodes(self):
        
        self.graph_builder.add_node("request_handler", request_handler_node)
        self.graph_builder.add_node("company_profiler_node", company_profiler_node)
        
        self.graph_builder.add_node(get_agent_node_name(AgentName.TECH_REVIEWER), tech_reviewer_node)
        self.graph_builder.add_node(get_agent_node_name(AgentName.COMMERCIAL_ANALYST), commercial_analyst_node)
        self.graph_builder.add_node(get_agent_node_name(AgentName.TEAM_ANALYST), team_analyst_node)

        self.graph_builder.add_node(ANALYSIS_AGGREGATOR_NODE, analysis_aggregator_node)


    def _build_edges(self):
        
        self.graph_builder.add_edge(START, "request_handler")
        
        self.graph_builder.add_edge("request_handler", "company_profiler_node")
    
        self.graph_builder.add_conditional_edges(
            "company_profiler_node", 
            analyst_fan_out_node, 
                [get_agent_node_name(agent) for agent in ANALYST_AGENTS]
            )

        for agent in ENABLED_ANALYST_AGENTS:
            self.graph_builder.add_edge(get_agent_node_name(agent), ANALYSIS_AGGREGATOR_NODE)
        
        self.graph_builder.add_edge(ANALYSIS_AGGREGATOR_NODE, END)

        
    def _compile_grap(self):
        
        self.compiled_graph = self.graph_builder.compile()
        

if __name__ == "__main__":
    
    graph = DueDiligence_Graph()
    print(graph)
    
    print(graph.compiled_graph.get_graph().draw_mermaid())
    
    state = DueDiligence_State()
    
    result = graph.compiled_graph.invoke(state)
    print(f"Res -> {result}")