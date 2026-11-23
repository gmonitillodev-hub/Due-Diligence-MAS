import asyncio

from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain.agents.structured_output import ToolStrategy

from due_diligence_mas.mas_definition.classes.company import AnalysisReview
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.langgraph import SUPERVISOR_NODE
from due_diligence_mas.mas_definition.constants.review import ANALYSIS_REVIEW_CRITERIA, TASK_CREATION_INSTRUCTIONS
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State, SupervisionState
from due_diligence_mas.mas_definition.providers.llm_provider import LLM_PROVIDER
from due_diligence_mas.mas_definition.tools.mcp_task import get_task_tools
from due_diligence_mas.mas_definition.utils.backstory_builder import backstory_builder
from due_diligence_mas.utils.logger import log_node as _log

MAX_TASKS = 2


def review_analysis(state: DueDiligence_State):
    """Completeness gate: an agent scores the aggregated analysis from 0 to 10 before the debate and, when it decides follow-up work is needed, creates tasks through the task manager MCP tools. MCP tools are async only, the graph is sync."""
    generic = "\n".join(state.company_profile.generic or []) if state.company_profile else ""
    content = f"COMPANY: {state.describe()}\n\nPROFILE:\n{generic}\n\nAGGREGATED ANALYSIS:\n{state.analysis_results}"
    review = asyncio.run(_review_analysis_agent(content))
    _log(SUPERVISOR_NODE, "analysis review", score=review.score, missing=len(review.missing))
    return {"supervision": SupervisionState(analysis_review=review)}


async def _review_analysis_agent(content: str) -> AnalysisReview:
    """Run the review agent with the task tools. Hard cap of one task per topic; no checkpointer, so it does not inherit the graph's sync SqliteSaver, which cannot run under ainvoke."""
    agent = create_agent(
        model=LLM_PROVIDER().get_chat_model(),
        tools=await get_task_tools(),
        system_prompt=backstory_builder(AgentName.ANALYST_SUPERVISOR.value),
        response_format=ToolStrategy(AnalysisReview),
        middleware=[ToolCallLimitMiddleware(tool_name="create_task", run_limit=MAX_TASKS)],
        checkpointer=False,
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content": f"{ANALYSIS_REVIEW_CRITERIA}\n\n{TASK_CREATION_INSTRUCTIONS}\n\n{content}"}]})
    _log(SUPERVISOR_NODE, "analysis review agent", tools_called=[m.name for m in result["messages"] if getattr(m, "type", "") == "tool"])
    return result["structured_response"]
