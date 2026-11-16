from due_diligence_mas.mas_definition.agents.spec import SpecAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class TeamAnalyst_Agent(SpecAgent):
    name = AgentName.TEAM_ANALYST
    tools = ("linkedin", "tavily_page_extractor",)

    tasks_def = {
        "main": TaskDef(
            description=(
                "Review the founding team and organization of the target company: {topic}. "
                "Start from the provided context (official URLs, findings, missing items): search only for information that is absent or listed as missing, and do not repeat searches already covered by the context. "
                "Use the team members, team page and LinkedIn URLs found during company profiling as starting points. "
                "Cover founder backgrounds, prior exits, founder-market fit, leadership, hiring signals and key-person risk. "
                "Use only public, verifiable information and mark unknowns as missing."
            ),
            expected_output="A markdown report with: a short summary; the findings as a list, each with its source URL, access date and whether it is verified, a company claim or to be confirmed; and a 'Missing information' list.",
        ),
    }
