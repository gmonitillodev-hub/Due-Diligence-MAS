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
        "search_depth": "advanced",
        "max_results": 5,
        "include_answer": False,
    },
    "profile_search": {
        "search_depth": "advanced",
        "max_results": 5,
        "include_answer": False,
    },
    "funding_search": {
        "name": "tavily_funding_news_search",
        "description": (
            "Search funding, revenue and financial news about a company, "
            "restricted to startup and financial news sources."
        ),
        "search_depth": "advanced",
        "topic": "news",
        "max_results": 7,
        "include_answer": False,
        "include_domains": FUNDING_DOMAINS,
    },
}


MAX_CONTENT_CHARS = 10000
BLOCKING_ERROR_CODES = ("401", "429", "432", "433")


class TavilyBlockingError(RuntimeError):
    """Tavily refuses every request (invalid key, rate or plan limit): retrying cannot work."""


def _raise_on_blocking_error(output):
    """langchain_tavily returns API errors as {"error": exception} text for the model, which retries until the tool call limit. Account level errors are raised instead; query errors (400) stay with the model."""
    error = output.get("error") if isinstance(output, dict) else None
    if error is not None and any(f"Error {code}" in str(error) for code in BLOCKING_ERROR_CODES):
        raise TavilyBlockingError(str(error))
    return output


def _truncate_results(output, max_chars: int = MAX_CONTENT_CHARS):
    """Cut the text of every result so tool outputs do not fill the agent context."""
    if isinstance(output, dict):
        for item in output.get("results") or []:
            for key in ("content", "raw_content"):
                if isinstance(item.get(key), str) and len(item[key]) > max_chars:
                    item[key] = item[key][:max_chars] + "... [truncated]"
    return output


class _TruncatedTavilySearch(TavilySearch):
    def _run(self, *args, **kwargs):
        return _truncate_results(_raise_on_blocking_error(super()._run(*args, **kwargs)))


class _TruncatedTavilyExtract(TavilyExtract):
    def _run(self, *args, **kwargs):
        return _truncate_results(_raise_on_blocking_error(super()._run(*args, **kwargs)))


def _tool_classes(framework: Framework):
    """(search, extract) tool classes of the framework, imported lazily so only the one in use is required."""
    match framework:
        case Framework.CREW_AI:
            return TavilySearchTool, TavilyExtractorTool
        case Framework.LANG_GRAPH:
            return _TruncatedTavilySearch, _TruncatedTavilyExtract
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
