from crewai_tools import TavilySearchTool, TavilyExtractorTool
from dotenv import load_dotenv

load_dotenv()

def get_tavily_tool(type: str):
  
    match type:
        
        case "search":
    
            return TavilySearchTool(
                search_depth="basic",
                max_results=3,
                include_answer=False,
            )
            
        case "page_extractor":
            return TavilyExtractorTool()
    

    