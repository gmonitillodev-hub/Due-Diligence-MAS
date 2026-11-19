from dotenv import load_dotenv
from due_diligence_mas.mas_definition.constants.common import Framework

load_dotenv()

APIFY_ACTORS = {
    "profile": "dev_fusion/linkedin-profile-scraper",
}


def _tool_class(framework: Framework):
    """Apify actor tool class of the framework, imported lazily so only the one in use is required."""
    match framework:
        case Framework.CREW_AI:
            from crewai_tools import ApifyActorsTool
            return ApifyActorsTool
        case Framework.LANG_GRAPH:
            from langchain_apify import ApifyActorsTool
            return ApifyActorsTool
        case _:
            raise ValueError(f"Unknown framework '{framework}'")


def get_linkedin_tool(tool_type: str = "profile", framework: Framework = Framework.CREW_AI):
    """LinkedIn tool backed by an Apify actor. tool_type: one of APIFY_ACTORS."""
    if tool_type not in APIFY_ACTORS:
        raise ValueError(f"Unknown Apify tool type '{tool_type}'. Available: {', '.join(APIFY_ACTORS)}")

    actor = APIFY_ACTORS[tool_type]
    # crewai_tools names the actor argument `actor_name`, langchain_apify `actor_id`
    argument = "actor_id" if framework == Framework.LANG_GRAPH else "actor_name"
    return _tool_class(framework)(**{argument: actor})
