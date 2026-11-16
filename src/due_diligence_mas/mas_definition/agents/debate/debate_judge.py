from due_diligence_mas.mas_definition.agents.spec import SpecAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class DebateJudge_Agent(SpecAgent):
    name = AgentName.DEBATE_JUDGE

    tasks_def = {
        "main": TaskDef(
            description=(
                "Judge the PRO/CONTRO debate on the target company, using the PRO and CONTRO cases received from the previous tasks. "
                "Weigh the strength of the PRO arguments against the severity of the CONTRO arguments, assess evidence quality, flag unsupported claims and critical missing data, decide whether risks are knowable, mitigable or deal-breaking, identify the central investment tension and whether further diligence is justified. "
                "Do not write the final memo."
            ),
            expected_output="A balanced preliminary judgement (SWOT analysis): evidence-quality assessment of both sides, central tension, risk classification, and a recommendation on further diligence, for the final memo to use.",
        ),
    }
