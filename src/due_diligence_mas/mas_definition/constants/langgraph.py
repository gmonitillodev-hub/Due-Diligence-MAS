import os

from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.utils.agent_names import get_agent_node_name, get_node_name

# Node names of the graph: always "<name>_node", built by the utils
REQUEST_HANDLER_NODE = get_node_name("request_handler")
PROFILER_NODE = get_agent_node_name(AgentName.COMPANY_PROFILER)
SUPERVISOR_NODE = get_node_name("supervisor")
FAN_OUT_NODE = get_node_name("analyst_fan_out")
TECH_REVIEWER_NODE = get_agent_node_name(AgentName.TECH_REVIEWER)
COMMERCIAL_ANALYST_NODE = get_agent_node_name(AgentName.COMMERCIAL_ANALYST)
TEAM_ANALYST_NODE = get_agent_node_name(AgentName.TEAM_ANALYST)
ANALYSIS_AGGREGATOR_NODE = get_node_name("analysis_aggregator")
HUMAN_REVIEW_NODE = get_node_name("human_review")
DEBATE_FORMATTER_NODE = get_agent_node_name(AgentName.DEBATE_FORMATTER)
OPPORTUNITY_ANALYST_NODE = get_agent_node_name(AgentName.OPPORTUNITY_ANALYST)
RISK_ANALYST_NODE = get_agent_node_name(AgentName.RISK_ANALYST)
DEBATE_JUDGE_NODE = get_agent_node_name(AgentName.DEBATE_JUDGE)
MEMO_WRITER_NODE = get_agent_node_name(AgentName.MEMO_WRITER)

# Analysts available in the graph, and the ones the fan-out dispatches
ANALYST_AGENTS = (AgentName.TECH_REVIEWER, AgentName.COMMERCIAL_ANALYST, AgentName.TEAM_ANALYST)
ENABLED_ANALYST_AGENTS = (AgentName.TECH_REVIEWER, AgentName.COMMERCIAL_ANALYST, AgentName.TEAM_ANALYST)

# Extra profiler runs the supervisor can request before the profile goes on as it is
MAX_PROFILE_REVISIONS = 2


def skip_debate_formatter() -> bool:
    """True (default) when the debate formatter is skipped: the debate works directly on the analysis results."""
    return os.getenv("SKIP_DEBATE_FORMATTER", "true").strip().lower() in ("1", "true", "yes", "on")
