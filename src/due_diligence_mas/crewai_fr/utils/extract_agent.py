from due_diligence_mas.constants.agents_definition import AGENTS

def extract_agent(agent_name: str) -> dict:
    
    """
       Extracts the agent's information from the AGENTS dictionary.
       
        Args:
            agent_name (str): The name of the agent to extract.
                   
        Returns:
            dict: A dictionary containing the agent's information. 
    """
    if agent_name not in AGENTS:
        raise KeyError(f"Unknown agent '{agent_name}'. Available: {', '.join(AGENTS)}")
    
    return AGENTS[agent_name]


def agent_limits(agent_name: str) -> dict:
    """Inference limits (max_iter, max_execution_time) to pass to the Agent constructor."""
    return dict(extract_agent(agent_name).get("limits", {}))
