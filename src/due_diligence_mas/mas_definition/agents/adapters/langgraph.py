from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.tools.github import github_repos
from due_diligence_mas.mas_definition.tools.apify import get_linkedin_tool
from due_diligence_mas.mas_definition.tools.tavily import get_tavily_tool
from langchain.agents import create_agent
from langchain.tools import tool

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


def build_agent(definition):
    return create_agent(
        model=LLM_PROVIDER().get_chat_model(),
        tools=_resolve_tools(definition.tools),
        system_prompt=definition.backstory,
        response_format=None,
        name=definition.spec["name"].lower().replace(" ", "_"),
    )


def build_tasks(definition, task_def, topic: str, context: list) -> list[dict]:
    """A LangGraph task is the user message sent to the agent; `context` holds previous outputs as text."""
    parts = [f"{definition.spec['goal']}\n\n{task_def.description.replace('{topic}', topic)}"]
    parts.append(f"Expected output:\n{task_def.expected_output}")
    if context:
        parts.append("Context:\n" + "\n\n".join(str(c) for c in context))
    return [{"role": "user", "content": "\n\n".join(parts)}]
