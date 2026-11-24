from due_diligence_mas.mas_definition.agents.dd_agent import DDAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class DebateFormatter_Agent(DDAgent):
    name = AgentName.DEBATE_FORMATTER

    tasks_def = {
        "main": TaskDef(
            description=(
                "Prepare the debate evidence pack from the following complete analysis: {topic}. "
                "Condense it into a single structured document: a company snapshot, deduplicated evidence items each with a unique ID, source and confidence level, a clear separation of facts, assumptions and missing data, and the initial tensions within the analysis. "
                "Do not add new facts or new analysis."
            ),
            expected_output="A structured debate pack with sections: company snapshot, evidence items (ID, statement, source, confidence), facts vs assumptions vs missing data, and initial tensions.",
        ),
    }
