from due_diligence_mas.mas_definition.agents.spec import SpecAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class CommercialAnalyst_Agent(SpecAgent):
    name = AgentName.COMMERCIAL_ANALYST
    tools = ("tavily_search", "tavily_funding_search", "tavily_page_extractor",)

    tasks_def = {
        "main": TaskDef(
            description=(
                "Review the commercial aspects of the target company: {topic}. "
                "Start from the provided context (official URLs, findings, missing items): search only for information that is absent or listed as missing, and do not repeat searches already covered by the context. "
                "Cover market, competitors, pricing, revenue model, go-to-market, traction and public funding. "
                "Stay within commercial topics: product/technology and team belong to other specialists."
            ),
            expected_output="A markdown report with: a short summary; the findings as a list, each with its source URL, access date and whether it is verified, a company claim or to be confirmed; and a 'Missing information' list.",
        ),
    }
