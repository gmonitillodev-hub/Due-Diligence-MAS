from due_diligence_mas.constants.agents_definition import AGENTS


def backstory_builder(agent_name: str) -> str:
    """
    Builds a backstory for the given agent name.

    Args:
        agent_name (str): The name of the agent.

    Returns:
        str: A backstory for the agent.

    Raises:
        KeyError: If the agent is not defined in agents_definition.
    """
    if agent_name not in AGENTS:
        raise KeyError(f"Unknown agent '{agent_name}'. Available: {', '.join(AGENTS)}")
    agent = AGENTS[agent_name]

    parts = [f"You are the {agent['name']}.", agent["description"]]
    if agent.get("responsibilities"):
        parts.append("Responsibilities:\n" + "\n".join(f"- {r}" for r in agent["responsibilities"]))
    if agent.get("constraints"):
        parts.append("Constraints:\n" + "\n".join(f"- {c}" for c in agent["constraints"]))
    return "\n\n".join(parts)
    
    