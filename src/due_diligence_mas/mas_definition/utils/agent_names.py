from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


def agent_slug(agent_name: AgentName | str) -> str:
    """Snake_case identifier of an agent, e.g. "Tech Reviewer" -> "tech_reviewer"."""
    value = agent_name.value if isinstance(agent_name, AgentName) else agent_name
    return value.lower().replace(" ", "_")


def get_node_name(name: str) -> str:
    """Name of a LangGraph node, always "<snake_case_name>_node", e.g. "request handler" -> "request_handler_node"."""
    slug = name.lower().replace(" ", "_")
    return slug if slug.endswith("_node") else f"{slug}_node"


def get_agent_node_name(agent_name: AgentName | str) -> str:
    """Name of the LangGraph node that runs the agent, e.g. "Tech Reviewer" -> "tech_reviewer_node"."""
    return get_node_name(agent_slug(agent_name))
