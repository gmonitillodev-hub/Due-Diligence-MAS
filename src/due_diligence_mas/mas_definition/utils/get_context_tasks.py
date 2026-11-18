def get_context_tasks(*agents) -> list:
    """
    Safely collects the tasks of one or more agent wrappers into a single list
    to be used as task context.

    Args:
        *agents: Agent wrappers exposing get_tasks(). None values and agents
            whose tasks have not been built yet are skipped.

    Returns:
        list: All the tasks of the given agents, in order; empty if none available.
    """
    tasks = []
    for agent in agents:
        if agent is None or not hasattr(agent, "tasks"):
            continue
        tasks.extend(agent.get_tasks() or [])
    return tasks
