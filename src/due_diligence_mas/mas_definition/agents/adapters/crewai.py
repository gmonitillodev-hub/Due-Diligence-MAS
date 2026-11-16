from crewai import Agent, Task

from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.tools.apify import get_linkedin_tool
from due_diligence_mas.mas_definition.tools.github import github_repos
from due_diligence_mas.mas_definition.tools.request_handler import get_current_context
from due_diligence_mas.mas_definition.tools.tavily import get_tavily_tool
from due_diligence_mas.mas_definition.crewai_fr.utils import is_verbose
from due_diligence_mas.mas_definition.providers.llm_provider import LLM_PROVIDER
from crewai.tools import tool

TOOLS = {
    "current_context": lambda: tool(get_current_context),
    "github_repos": lambda: tool(github_repos),
    "linkedin": lambda: get_linkedin_tool("profile", Framework.CREW_AI),
    "tavily_search": lambda: get_tavily_tool("search"),
    "tavily_funding_search": lambda: get_tavily_tool("funding_search"),
    "tavily_profile_search": lambda: get_tavily_tool("profile_search"),
    "tavily_page_extractor": lambda: get_tavily_tool("page_extractor"),
}


def build_agent(definition) -> Agent:
    return Agent(
        role=definition.spec["name"],
        goal=definition.spec["goal"],
        backstory=definition.backstory,
        llm=LLM_PROVIDER().get_llm(),
        tools=[TOOLS[key]() for key in definition.tools],
        allow_delegation=definition.delegation,
        verbose=is_verbose("agent"),
        max_retry_limit=2,
        **definition.crewai_kwargs(),
        **definition.limits,
    )


def build_tasks(definition, task_def, topic: str, context: list) -> list[Task]:
    return [
        Task(
            description=task_def.description.replace("{topic}", topic),
            expected_output=task_def.expected_output,
            agent=definition.agent if task_def.bind_agent else None,
            output_pydantic=task_def.output_schema,
            context=context,
        )
    ]
