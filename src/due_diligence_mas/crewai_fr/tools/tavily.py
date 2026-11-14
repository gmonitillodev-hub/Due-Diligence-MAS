from crewai_tools import TavilySearchTool, TavilyExtractorTool
from dotenv import load_dotenv

load_dotenv()

FUNDING_DOMAINS = [
    "finsmes.com",
    "tech.eu",
    "news.crunchbase.com",
    "startupitalia.eu",
    "economyup.it",
]

def get_tavily_tool(type: str):
  
    match type:
        
        case "search":
    
            return TavilySearchTool(
                search_depth="basic",
                max_results=3,
                include_answer=False,
            )

        # Deeper search for the Company Profiler, who feeds all other specialists
        case "profile_search":
            return TavilySearchTool(
                search_depth="advanced",
                max_results=6,
                include_answer=False,
            )

        # Search restricted to funding/financial news sources
        case "funding_search":
            return TavilySearchTool(
                name="Tavily Funding News Search",
                description=(
                    "Search funding, revenue and financial news about a company, "
                    "restricted to startup and financial news sources."
                ),
                search_depth="basic",
                topic="news",
                max_results=5,
                include_answer=False,
                include_domains=FUNDING_DOMAINS,
            )
            
        case "page_extractor":
            return TavilyExtractorTool()

        case _:
            raise ValueError(f"Unknown Tavily tool type '{type}'")
