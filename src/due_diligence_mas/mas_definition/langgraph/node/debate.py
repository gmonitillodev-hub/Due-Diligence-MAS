import time

from due_diligence_mas.mas_definition.agents.debate.debate_formatter import DebateFormatter_Agent
from due_diligence_mas.mas_definition.agents.debate.debate_judge import DebateJudge_Agent
from due_diligence_mas.mas_definition.agents.debate.opportunity_analyst import OpportunityAnalyst_Agent
from due_diligence_mas.mas_definition.agents.debate.risk_analyst import RiskAnalyst_Agent
from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State
from due_diligence_mas.mas_definition.utils.agent_names import get_agent_node_name
from due_diligence_mas.mas_definition.langgraph.node.node_log import log_node as _log


def _run_debate_agent(agent_cls, topic: str, context: list[str]) -> str:
    """Build the agent and its task from the topic and the previous debate outputs, and return its report."""
    node = get_agent_node_name(agent_cls.name)
    _log(node, "start", topic_chars=len(topic), context_items=len(context))
    t0 = time.perf_counter()

    debate_agent = agent_cls(framework=Framework.LANG_GRAPH)
    debate_agent.build_tasks(topic, context)

    agent = debate_agent.get_agent()
    _log(node, "agent built", tools=list(debate_agent.tools))

    result = agent.invoke(
                {
                    "messages": debate_agent.get_tasks()
                },
                #config=self.checkpointer_config,
                #context=session_data,
            )
    report = result["messages"][-1].content

    _log(node, "end", elapsed_s=round(time.perf_counter() - t0, 2))
    return report


def debate_formatter_node(state: DueDiligence_State):
    
    pack = _run_debate_agent(DebateFormatter_Agent, state.analysis_results or "", [])
    return {"debate_pack": pack}


def _debate_context(state: DueDiligence_State) -> str:
    """Debate input: the formatter pack, or the analysis results when the formatter is skipped."""
    return state.debate_pack or state.analysis_results or ""


def opportunity_analyst_node(state: DueDiligence_State):
    
    pro_case = _run_debate_agent(OpportunityAnalyst_Agent, "", [_debate_context(state)])
    return {"pro_case": pro_case}


def risk_analyst_node(state: DueDiligence_State):
    
    contro_case = _run_debate_agent(RiskAnalyst_Agent, "", [_debate_context(state), state.pro_case])
    return {"contro_case": contro_case}


def debate_judge_node(state: DueDiligence_State):
    
    judgement = _run_debate_agent(DebateJudge_Agent, "", [state.pro_case, state.contro_case])
    return {"debate_results": judgement}
