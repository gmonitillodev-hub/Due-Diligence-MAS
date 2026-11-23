

from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.tools.github import github_repos
from due_diligence_mas.mas_definition.tools.apify import get_linkedin_tool
from due_diligence_mas.mas_definition.tools.tavily import get_tavily_tool
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain.agents.structured_output import ToolStrategy


from due_diligence_mas.mas_definition.utils.agent_names import agent_slug
from due_diligence_mas.mas_definition.tools.request_handler import get_current_context
from due_diligence_mas.mas_definition.providers.llm_provider import LLM_PROVIDER

TOOLS = {
    "current_context": lambda: tool(get_current_context),
    "github_repos": lambda: tool(github_repos),
    "linkedin": lambda: get_linkedin_tool(framework=Framework.LANG_GRAPH),
    "tavily_search": lambda: get_tavily_tool("search", Framework.LANG_GRAPH),
    "tavily_funding_search": lambda: get_tavily_tool("funding_search", Framework.LANG_GRAPH),
    "tavily_profile_search": lambda: get_tavily_tool("profile_search", Framework.LANG_GRAPH),
    "tavily_page_extractor": lambda: get_tavily_tool("page_extractor", Framework.LANG_GRAPH),
}


def _resolve_tools(keys):
    missing = [k for k in keys if k not in TOOLS]
    if missing:
        raise NotImplementedError(f"No LangChain implementation yet for tools: {', '.join(missing)}")
    return [TOOLS[k]() for k in keys]


def _limit_middleware(definition):
    """Cap tool calls per run with the agent's max_iter, as CrewAI does; once reached the model must answer with what it has."""
    max_iter = definition.limits.get("max_iter")
    return [ToolCallLimitMiddleware(run_limit=max_iter)] if max_iter else []


def build_agent(definition, task):
    
    output_schema = definition.tasks_def[task].output_schema if definition.tasks_def[task] else None

    return create_agent(
        model=LLM_PROVIDER().get_chat_model(),
        tools=_resolve_tools(definition.tools),
        system_prompt=definition.backstory,
        response_format=ToolStrategy(output_schema) if output_schema else None,
        middleware=_limit_middleware(definition),
        name=agent_slug(definition.spec["name"]),
    )


def build_tasks(definition, task_def, topic: str, context: list) -> list[dict]:
    """A LangGraph task is the user message sent to the agent; `context` holds previous outputs as text."""
    parts = [f"{task_def.description.replace('{topic}', topic)}"]
    parts.append(f"Goal: {definition.spec['goal']}")
    parts.append(f"Expected output:\n{task_def.expected_output}")
    if context:
        parts.append("Context:\n" + "\n\n".join(str(c) for c in context))
    return [{"role": "user", "content": "\n\n".join(parts)}]
