from due_diligence_mas.mas_definition.agents.analysts.company_profiler import CompanyProfiler_Agent
from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State

def company_profiler_node(state: DueDiligence_State):
    
    profiler = CompanyProfiler_Agent(framework=Framework.LANG_GRAPH)
        
    profiler.build_tasks(topic=state.company_info.describe())
    
    agent = profiler.get_agent()
        
    result = agent.invoke(
            {
                "messages": profiler.get_tasks()
            },
            #config=self.checkpointer_config,
            #context=session_data,
        )
    
    return {"company_profile": result["structured_response"]}
    