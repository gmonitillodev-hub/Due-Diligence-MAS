from due_diligence_mas.mas_definition.agents.spec import SpecAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class TechReviewer_Agent(SpecAgent):
    name = AgentName.TECH_REVIEWER
    tools = ("github_repos", "tavily_page_extractor",)

    tasks_def = {
        "main": TaskDef(
            description=(
                "Review the technology aspects of the target company: {topic}. "
                "Start from the provided context (official URLs, findings, missing items): search only for information that is absent or listed as missing, and do not repeat searches already covered by the context. "
                "If the company has an official public GitHub organization (linked from its website or docs), use the GitHub repositories tool with that owner to gather open-source evidence. "
                "Do not guess organizations: if none is confirmed, report GitHub signals as unavailable.Mark as To be confirmed all data fetched from GitHub.Perform a first match to ensure that all data are related actually to the company"
            ),
            expected_output="A markdown report with: a short summary; the findings as a list, each with its source URL, access date and whether it is verified, a company claim or to be confirmed; and a 'Missing information' list.",
        ),
    }
