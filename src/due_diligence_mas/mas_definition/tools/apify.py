from dotenv import load_dotenv
from crewai_tools import ApifyActorsTool
from langchain_apify import ApifyActorsTool
from due_diligence_mas.mas_definition.constants.common import Framework

load_dotenv()

APIFY_CONFIGS = {
    "profile": {"actor_name": "dev_fusion/linkedin-profile-scraper"},
}


def _tool_class(framework: Framework):
    """Apify actor tool class of the framework, imported lazily so only the one in use is required."""
    match framework:
        case Framework.CREW_AI:
            return ApifyActorsTool
        case Framework.LANG_GRAPH:
            return ApifyActorsTool
        case _:
            raise ValueError(f"Unknown framework '{framework}'")


def get_linkedin_tool(tool_type: str = "profile", framework: Framework = Framework.CREW_AI):
    """LinkedIn tool backed by an Apify actor. tool_type: one of APIFY_CONFIGS."""
    if tool_type not in APIFY_CONFIGS:
        raise ValueError(f"Unknown Apify tool type '{tool_type}'. Available: {', '.join(APIFY_CONFIGS)}")

    return _tool_class(framework)(**APIFY_CONFIGS[tool_type])
