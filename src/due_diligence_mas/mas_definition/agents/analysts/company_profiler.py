from due_diligence_mas.mas_definition.classes import CompanyProfile
from due_diligence_mas.mas_definition.agents.dd_agent import DDAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class CompanyProfiler_Agent(DDAgent):
    name = AgentName.COMPANY_PROFILER
    tools = ("tavily_profile_search", "tavily_page_extractor", "current_context",)

    tasks_def = {
        "main": TaskDef(
            description=(
                "Profile the following target company: {topic}. "
                "Extract all possible informations through websites, using also sitemaps to get all relevant pages. "
                "Always try the company's pages that usually hold key facts (about, team, company, careers, contact, footer links to GitHub and LinkedIn) before concluding that an item is missing. "
                "If the work is delegated more than once, the final answer must cumulate the facts of ALL the executions, in particular the earliest ones: never report only the result of the last execution, and never drop an entry already collected. "
                "If a follow-up request lists items already found, do not repeat them: search only the missing ones, and report each item you still cannot find as 'missing (not found after search)'."
            ),
            expected_output=(
                "English, no markdown, in four fields: generic, tech, commercial, team. "
                "Each field is a list with one entry per fact or gap. "
                "Be exhaustive: include every fact collected, without summarizing or merging entries; there is no length limit. "
                "Every fact entry has the form: fact | source URL | access date (YYYY-MM-DD) | verified, claimed or to be confirmed. "
                "The source must be a URL, never only a publication name.\n"
                "generic: official website, what the company does, sector, headquarters, founding year, products or services, value proposition, target customers, clients/partners/case studies, geography.\n"
                "tech (for technology review): official GitHub organization URL (only if linked from the company site or docs), documentation/API/pricing/product page URLs, technology claims found, and what is still missing.\n"
                "commercial (for commercial analysis): clients, pricing, market and traction signals, funding or press mentions found, and what is still missing.\n"
                "team (for team analysis): team page URL, LinkedIn company page URL, names and roles of visible team members, and what is still missing."
            ),
            output_schema=CompanyProfile,
        ),
    }
