from due_diligence_mas.mas_definition.agents.spec import SpecAgent
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class AnalysisManager(SpecAgent):
    """Manager of the CrewAI hierarchical Analyst Crew: it has no task of its own, it only delegates."""

    name = AgentName.ANALYSIS_MANAGER
    delegation = True
