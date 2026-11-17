
from due_diligence_mas.mas_definition.agents.analysts.commercial_analyst import CommercialAnalyst_Agent
from due_diligence_mas.mas_definition.agents.analysts.team_analyst import TeamAnalyst_Agent
from due_diligence_mas.mas_definition.agents.analysts.tech_reviewer import TechReviewer_Agent
from due_diligence_mas.mas_definition.classes.company import CompanyProfile
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.constants.langgraph import ENABLED_ANALYST_AGENTS, FAN_OUT_NODE
from due_diligence_mas.mas_definition.utils.agent_names import get_agent_node_name
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State
from langgraph.types import Send
import time
from due_diligence_mas.mas_definition.langgraph.node.node_log import log_node as _log


def analyst_fan_out_node(state: DueDiligence_State):
    
    _log(FAN_OUT_NODE, "start", enabled_agents=[a.value for a in ENABLED_ANALYST_AGENTS])

    send_list: list[Send] = []

    for agent in ENABLED_ANALYST_AGENTS:
        
        node_name = get_agent_node_name(agent_name=agent)
        send_list.append(
            Send(
                node_name,
                state
            )
        )
        _log(FAN_OUT_NODE, "dispatch", target=node_name)
        
    return send_list
            
def tech_reviewer_node(state: DueDiligence_State):
    
    tech_reviewer = TechReviewer_Agent(framework=Framework.LANG_GRAPH)
    node = get_agent_node_name(AgentName.TECH_REVIEWER)
    _log(node, "start", company=state.company_info.company_name if state.company_info else None, has_profile=state.company_profile is not None)
    t0 = time.perf_counter()
    tech_reviewer.build_tasks(state.topic_for("tech"))
    
    agent = tech_reviewer.get_agent()
    _log(node, "agent built", tools=list(tech_reviewer.tools), topic_chars=len(state.topic_for("tech")))
    
    result = agent.invoke(
                {
                    "messages": tech_reviewer.get_tasks()
                },
                #config=self.checkpointer_config,
                #context=session_data,
            )
    _log(node, "end", elapsed_s=round(time.perf_counter() - t0, 2))
    return {"company_profile": CompanyProfile(tech=[result["messages"][-1].content])}

def commercial_analyst_node(state: DueDiligence_State):
    
    commercial_analyst = CommercialAnalyst_Agent(framework=Framework.LANG_GRAPH)
    node = get_agent_node_name(AgentName.COMMERCIAL_ANALYST)
    _log(node, "start", company=state.company_info.company_name if state.company_info else None, has_profile=state.company_profile is not None)
    t0 = time.perf_counter()
    commercial_analyst.build_tasks(state.topic_for("commercial"))
    
    agent = commercial_analyst.get_agent()
    _log(node, "agent built", tools=list(commercial_analyst.tools), topic_chars=len(state.topic_for("commercial")))

    result = agent.invoke(
                {
                    "messages": commercial_analyst.get_tasks()
                },
                #config=self.checkpointer_config,
                #context=session_data,
            )
    _log(node, "end", elapsed_s=round(time.perf_counter() - t0, 2))
    return {"company_profile": CompanyProfile(commercial=[result["messages"][-1].content])}

def team_analyst_node(state: DueDiligence_State):
    
    team_analyst = TeamAnalyst_Agent(framework=Framework.LANG_GRAPH)    
    node = get_agent_node_name(AgentName.TEAM_ANALYST)
    _log(node, "start", company=state.company_info.company_name if state.company_info else None, has_profile=state.company_profile is not None)
    t0 = time.perf_counter()
    team_analyst.build_tasks(state.topic_for("team"))
    
    agent = team_analyst.get_agent()
    _log(node, "agent built", tools=list(team_analyst.tools), topic_chars=len(state.topic_for("team")))

    result = agent.invoke(
                {
                    "messages": team_analyst.get_tasks()
                },
                #config=self.checkpointer_config,
                #context=session_data,
            )
    _log(node, "end", elapsed_s=round(time.perf_counter() - t0, 2))
    return {"company_profile": CompanyProfile(team=[result["messages"][-1].content])}
