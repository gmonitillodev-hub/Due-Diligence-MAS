from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State
from due_diligence_mas.mas_definition.langgraph.node.request_handler import request_handler_node
from langgraph.graph import StateGraph, START, END


class DueDiligence_Graph():
    
    def __init__(self):
        
        self.graph_builder = StateGraph(DueDiligence_State)
        
        self._build_nodes()
        self._build_edges()
        self._compile_grap()
        
    def _build_nodes(self):
        
        self.graph_builder.add_node("request_handler", request_handler_node)

    def _build_edges(self):
        
        self.graph_builder.add_edge(START, "request_handler")
        self.graph_builder.add_edge("request_handler", END)
        
    def _compile_grap(self):
        
        self.compiled_graph = self.graph_builder.compile()
        

if __name__ == "__main__":
    
    graph = DueDiligence_Graph()
    print(graph)
    
    print(graph.compiled_graph.get_graph().draw_mermaid())
    
    state = DueDiligence_State()
    
    graph.compiled_graph.invoke(state)