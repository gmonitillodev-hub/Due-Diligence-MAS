from due_diligence_mas.mas_definition.agents.dd_agent import DDAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.research import ANALYST_REPORT_FORMAT, CONTEXT_FIRST


class TechReviewer_Agent(DDAgent):
    name = AgentName.TECH_REVIEWER
    tools = ("tavily_search", "github_repos", "tavily_page_extractor",)

    tasks_def = {
        "main": TaskDef(
            description=(
                "Review the technology aspects of the target company: {topic}. "
                f"{CONTEXT_FIRST} "
                "If the company has an official GitHub organization (linked from its website or docs), use the GitHub repositories tool with that owner to gather open-source evidence; "
                "do not guess organizations, and if none is confirmed report the GitHub signals as unavailable. "
                "Check that the repositories really belong to the company and mark all GitHub data as to be confirmed."
            ),
            expected_output=ANALYST_REPORT_FORMAT,
        ),
    }
