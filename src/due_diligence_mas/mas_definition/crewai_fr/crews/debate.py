from due_diligence_mas.mas_definition.agents.debate.debate_formatter import DebateFormatter_Agent
from due_diligence_mas.mas_definition.agents.debate.debate_judge import DebateJudge_Agent
from due_diligence_mas.mas_definition.agents.debate.opportunity_analyst import OpportunityAnalyst_Agent
from due_diligence_mas.mas_definition.agents.debate.risk_analyst import RiskAnalyst_Agent
from due_diligence_mas.mas_definition.crewai_fr.crews.base import BaseCrew


class DebateCrew(BaseCrew):
    """
    Opportunity vs. risk debate, optionally preceded by a formatter, closed by the judge.
    """

    name = "Debate Crew"

    def __init__(self, args: dict | None = None, need_formatter: bool = True):
        self.topic = args or {}
        self.need_formatter = need_formatter
        super().__init__()

    def _setup(self):
        formatter_tasks = []
        if self.need_formatter:
            formatter = self.add(DebateFormatter_Agent(), self.topic)
            formatter_tasks = formatter.get_tasks()

        opportunity = self.add(OpportunityAnalyst_Agent(), self.topic, context=formatter_tasks)
        risk = self.add(
            RiskAnalyst_Agent(), self.topic, context=formatter_tasks + opportunity.get_tasks()
        )
        self.add(
            DebateJudge_Agent(), self.topic, context=opportunity.get_tasks() + risk.get_tasks()
        )
