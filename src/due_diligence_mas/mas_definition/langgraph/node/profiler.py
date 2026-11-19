from due_diligence_mas.mas_definition.agents.analysts.company_profiler import CompanyProfiler_Agent
from due_diligence_mas.mas_definition.classes.company import CompanyProfile
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.constants.langgraph import PROFILER_NODE
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State, SupervisionState
from due_diligence_mas.utils.logger import log_node as _log

def company_profiler_node(state: DueDiligence_State):
    profiler = CompanyProfiler_Agent(framework=Framework.LANG_GRAPH)
    review = state.supervision.profile_review
    revision = review is not None and not review.approved
    _log(PROFILER_NODE, "start", revision=state.supervision.profile_revisions if revision else 0)

    context = []
    if revision:
        context = [f"PREVIOUS PROFILE:\n{state.company_profile.model_dump_json(indent=2)}", f"SUPERVISOR FEEDBACK (fix these issues, keep the correct facts):\n{review.feedback}\n" + "\n".join(f"- {i}" for i in review.issues)]
    profiler.build_tasks(topic=state.company_info.describe(), context=context)

    # The agent's ToolStrategy(CompanyProfile) fills `structured_response`
    result = profiler.get_agent().invoke({"messages": profiler.get_tasks()})

    return {
        "company_profile": result["structured_response"],
        "profile_iterations": [result["structured_response"]],
        "supervision": SupervisionState(profile_revisions=state.supervision.profile_revisions + 1),
    }
