from due_diligence_mas.mas_definition.agents.spec import SpecAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.research import ANALYST_REPORT_FORMAT, CONTEXT_FIRST


class TeamAnalyst_Agent(SpecAgent):
    name = AgentName.TEAM_ANALYST
    tools = ("tavily_search", "linkedin", "tavily_page_extractor",)

    tasks_def = {
        "main": TaskDef(
            description=(
                "Review the founding team and organization of the target company: {topic}. "
                f"{CONTEXT_FIRST} "
                "Use the team members, team page and LinkedIn URLs found during company profiling as starting points. "
                "Use only public, verifiable information."
            ),
            expected_output=ANALYST_REPORT_FORMAT,
        ),
    }
