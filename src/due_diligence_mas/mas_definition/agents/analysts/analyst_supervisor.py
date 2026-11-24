from due_diligence_mas.mas_definition.agents.dd_agent import DDAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class AnalystSupervisor(DDAgent):
    name = AgentName.ANALYST_SUPERVISOR
    delegation = True

    tasks_def = {
        "main": TaskDef(
            description="Considering the company profile in the context.",
            expected_output="A markdown analysis report with one section per specialist, keeping their findings unchanged, followed by 'Resolved conflicts' and 'Missing information' sections.",
            bind_agent=False,
        ),
    }
