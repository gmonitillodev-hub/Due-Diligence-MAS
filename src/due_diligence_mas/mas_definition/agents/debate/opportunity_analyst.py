from due_diligence_mas.mas_definition.agents.dd_agent import DDAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class OpportunityAnalyst_Agent(DDAgent):
    name = AgentName.OPPORTUNITY_ANALYST

    tasks_def = {
        "main": TaskDef(
            description=(
                "Build the PRO case for the target company. "
                "Using only the formatted debate document received from the previous task, identify the strongest evidence-backed reasons to continue diligence or invest: positive signals, market timing, commercial upside, product strengths, technical defensibility, founder-market fit and traction. "
                "Reference evidence IDs for every argument, flag arguments resting on weak evidence, do not invent facts or search externally, and do not ignore missing data."
            ),
            expected_output="A structured PRO case: ranked strengths and reasons to continue diligence, each linked to evidence IDs with an evidence-strength note.",
        ),
    }
