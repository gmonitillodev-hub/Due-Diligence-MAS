import os

from crewai import Process

from due_diligence_mas.mas_definition.agents.analysts.analysis_manager import AnalysisManager
from due_diligence_mas.mas_definition.agents.analysts.commercial_analyst import CommercialAnalyst_Agent
from due_diligence_mas.mas_definition.agents.analysts.company_profiler import CompanyProfiler_Agent
from due_diligence_mas.mas_definition.agents.analysts.team_analyst import TeamAnalyst_Agent
from due_diligence_mas.mas_definition.agents.analysts.tech_reviewer import TechReviewer_Agent
from due_diligence_mas.mas_definition.agents.writer.memo_writer import MemoWriter_Agent
from due_diligence_mas.mas_definition.classes import CompanyInfo
from due_diligence_mas.mas_definition.crewai_fr.crews.base import BaseCrew
from due_diligence_mas.utils.logger import log_crew

# Keep in sync with the Profiler delegation rule in the "Analysis Manager" constraints
MAX_PROFILER_DELEGATIONS = 4

# Async specialist tasks under the hierarchical manager fail with "Executor is already running" (OP-01);
# set ANALYST_ASYNC=false to run them one after another.
ANALYST_ASYNC = os.getenv("ANALYST_ASYNC", "true").lower() == "true"


class AnalystCrew(BaseCrew):
    """
    Hierarchical crew: the manager has no task of its own and delegates the profiling, the three specialist
    tasks and the final aggregation, which the Memo Writer produces as the intermediate analysis report.
    Specialist tasks are asynchronous and the manager chooses the context it passes to the coworkers.
    """

    name = "Analyst Crew"
    process = Process.hierarchical

    def __init__(self, company_info: CompanyInfo):
        self.topic = company_info.describe()
        super().__init__()

    def _setup(self):
        self.manager = AnalysisManager()

        profiler = self.add(CompanyProfiler_Agent(), self.topic)
        self.profiler = profiler
        # Free-text output: the structured conversion is needed only by LangGraph
        for task in profiler.get_tasks():
            task.output_pydantic = None

        specialists = [self.add(agent_cls(), self.topic) for agent_cls in
                       (TechReviewer_Agent, CommercialAnalyst_Agent, TeamAnalyst_Agent)]
        specialist_tasks = [task for agent in specialists for task in agent.get_tasks()]
        for task in specialist_tasks:
            task.async_execution = ANALYST_ASYNC

        # The report is the Memo Writer's aggregation; the manager has no task of its own
        self.add(MemoWriter_Agent(), self.topic, context=profiler.get_tasks() + specialist_tasks, key="aggregation")

    def build_crew(self):
        super().build_crew()

        # The manager runs every task and would otherwise use the coworkers' tools itself;
        # __dict__ bypasses the validator, which would copy the tools back.
        for task in self.crew.tasks:
            task.__dict__["tools"] = []

    def run_crew(self) -> str:
        """Returns the intermediate analysis report in markdown."""
        result = super().run_crew().raw
        self._log_profiler_delegations()
        return result

    def _log_profiler_delegations(self):
        """The cap on the Profiler delegations is a manager prompt rule, not enforced by CrewAI: log when it is exceeded."""
        executions = len(self.profiler.raw_outputs)
        log_crew(self.name, "profiler_delegations", executions=executions, max=MAX_PROFILER_DELEGATIONS,
                 exceeded=executions > MAX_PROFILER_DELEGATIONS)
