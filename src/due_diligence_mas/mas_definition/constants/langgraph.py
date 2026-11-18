import os

from due_diligence_mas.mas_definition.constants.agents_definition import AgentName

FAN_OUT_NODE = "analyst_fan_out_node"
ANALYSIS_AGGREGATOR_NODE = "analysis_aggregator_node"
MEMO_WRITER_NODE = "memo_writer_node"

# Analysts available in the graph, and the ones the fan-out dispatches
ANALYST_AGENTS = (AgentName.TECH_REVIEWER, AgentName.COMMERCIAL_ANALYST, AgentName.TEAM_ANALYST)
ENABLED_ANALYST_AGENTS = (AgentName.TECH_REVIEWER, AgentName.COMMERCIAL_ANALYST)

# Extra profiler runs the supervisor can request before the profile goes on as it is
MAX_PROFILE_REVISIONS = 2


def skip_debate_formatter() -> bool:
    """True (default) when the debate formatter is skipped: the debate works directly on the analysis results."""
    return os.getenv("SKIP_DEBATE_FORMATTER", "true").strip().lower() in ("1", "true", "yes", "on")
