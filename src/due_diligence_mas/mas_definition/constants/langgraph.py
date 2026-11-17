from due_diligence_mas.mas_definition.constants.agents_definition import AgentName

FAN_OUT_NODE = "analyst_fan_out_node"
ANALYSIS_AGGREGATOR_NODE = "analysis_aggregator_node"

# Analysts available in the graph, and the ones the fan-out dispatches
ANALYST_AGENTS = (AgentName.TECH_REVIEWER, AgentName.COMMERCIAL_ANALYST, AgentName.TEAM_ANALYST)
ENABLED_ANALYST_AGENTS = (AgentName.TECH_REVIEWER, AgentName.COMMERCIAL_ANALYST)
