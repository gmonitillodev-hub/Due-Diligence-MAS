from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


def agent_slug(agent_name: AgentName | str) -> str:
    """Snake_case identifier of an agent, e.g. "Tech Reviewer" -> "tech_reviewer"."""
    value = agent_name.value if isinstance(agent_name, AgentName) else agent_name
    return value.lower().replace(" ", "_")


def get_agent_node_name(agent_name: AgentName | str) -> str:
    """Name of the LangGraph node that runs the agent, e.g. "Tech Reviewer" -> "tech_reviewer_node"."""
    return f"{agent_slug(agent_name)}_node"
