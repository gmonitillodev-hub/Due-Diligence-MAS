from dotenv import load_dotenv

from due_diligence_mas.mas_definition.constants.common import Framework
from crewai_tools import TavilyExtractorTool, TavilySearchTool
from langchain_tavily import TavilyExtract, TavilySearch

load_dotenv()

FUNDING_DOMAINS = [
    "finsmes.com",
    "tech.eu",
    "news.crunchbase.com",
    "startupitalia.eu",
    "economyup.it",
]

SEARCH_CONFIGS = {
    "search": {
        "search_depth": "basic",
        "max_results": 3,
        "include_answer": False,
    },
    "profile_search": {
        "search_depth": "advanced",
        "max_results": 6,
        "include_answer": False,
    },
    "funding_search": {
        "name": "tavily_funding_news_search",
        "description": (
            "Search funding, revenue and financial news about a company, "
            "restricted to startup and financial news sources."
        ),
        "search_depth": "basic",
        "topic": "news",
        "max_results": 5,
        "include_answer": False,
        "include_domains": FUNDING_DOMAINS,
    },
}


def _tool_classes(framework: Framework):
    """(search, extract) tool classes of the framework, imported lazily so only the one in use is required."""
    match framework:
        case Framework.CREW_AI:
            return TavilySearchTool, TavilyExtractorTool
        case Framework.LANG_GRAPH:
            return TavilySearch, TavilyExtract
        case _:
            raise ValueError(f"Unknown framework '{framework}'")


def get_tavily_tool(tool_type: str, framework: Framework = Framework.CREW_AI):
    """Tavily tool for the framework. tool_type: page_extractor or one of SEARCH_CONFIGS."""
    search_cls, extract_cls = _tool_classes(framework)

    if tool_type == "page_extractor":
        return extract_cls()

    if tool_type not in SEARCH_CONFIGS:
        raise ValueError(f"Unknown Tavily tool type '{tool_type}'. Available: page_extractor, {', '.join(SEARCH_CONFIGS)}")

    return search_cls(**SEARCH_CONFIGS[tool_type])
