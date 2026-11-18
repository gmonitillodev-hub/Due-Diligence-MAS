from due_diligence_mas.mas_definition.agents.analysts.commercial_analyst import CommercialAnalyst_Agent
from due_diligence_mas.mas_definition.agents.analysts.team_analyst import TeamAnalyst_Agent
from due_diligence_mas.mas_definition.agents.analysts.tech_reviewer import TechReviewer_Agent
from due_diligence_mas.mas_definition.agents.writer.memo_writer import MemoWriter_Agent
from due_diligence_mas.mas_definition.classes import ProfiledCompany
from due_diligence_mas.mas_definition.crewai_fr.crews.base import BaseCrew


class AnalystCrew(BaseCrew):
    """
    Sequential crew: the specialists run first, then the Memo Writer aggregates their reports.
    """

    name = "Analyst Crew"

    def __init__(self, company: ProfiledCompany, required_agents: list[str] | None = None):
        self.company = company
        self.required_agents = required_agents or []
        super().__init__()

    def _is_required(self, agent_cls) -> bool:
        return not self.required_agents or agent_cls.name.value in self.required_agents

    def _setup(self):
        specialists = [
            (TechReviewer_Agent, "tech"),
            (CommercialAnalyst_Agent, "commercial"),
            (TeamAnalyst_Agent, "team"),
        ]
        added = [
            self.add(agent_cls(), self.company.topic_for(area))
            for agent_cls, area in specialists
            if self._is_required(agent_cls)
        ]

        # Aggregation, run by the memo writer on all the specialists' outputs
        specialist_tasks = [task for agent in added for task in agent.get_tasks()]
        self.memo_writer = self.add(
            MemoWriter_Agent(), self.company.profile_topic(), context=specialist_tasks, key="aggregation"
        )

    def run_crew(self) -> str:
        """Returns the consolidated analysis in markdown."""
        return super().run_crew().raw
