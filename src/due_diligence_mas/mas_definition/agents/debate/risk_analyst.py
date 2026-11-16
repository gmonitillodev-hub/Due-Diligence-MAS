from due_diligence_mas.mas_definition.agents.spec import SpecAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class RiskAnalyst_Agent(SpecAgent):
    name = AgentName.RISK_ANALYST

    tasks_def = {
        "main": TaskDef(
            description=(
                "Build the CONTRO case for the target company. "
                "Using the formatted debate document and the PRO arguments received from the previous tasks, challenge weak or unsupported PRO claims and surface commercial, market, product/technical, team and financial risks, critical missing evidence and possible deal breakers. "
                "Reference evidence IDs or explicitly cite missing data for every argument; be rigorous, not merely pessimistic."
            ),
            expected_output="A structured CONTRO case: rebuttals to PRO arguments, ranked risks and deal breakers, and critical missing data, each linked to evidence IDs.",
        ),
    }
