from crewai import Process

from due_diligence_mas.mas_definition.agents.analysts.analyst_supervisor import AnalystSupervisor
from due_diligence_mas.mas_definition.agents.analysts.company_profiler import CompanyProfiler_Agent
from due_diligence_mas.mas_definition.classes import CompanyInfo
from due_diligence_mas.mas_definition.crewai_fr.crews.base import BaseCrew


class ProfilerCrew(BaseCrew):
    """
    Crew that profiles the target company (hierarchical, supervisor as manager).
    """

    name = "Profiler Crew"
    process = Process.hierarchical

    def __init__(self, company_info: CompanyInfo):
        self.topic = company_info.describe()
        super().__init__()

    def _setup(self):
        self.manager = AnalystSupervisor()
        self.profiler = self.add(CompanyProfiler_Agent(), self.topic)

    def build_crew(self):
        """Build the crew, then strip tools from the tasks: the manager runs every task and would otherwise use the profiler's tools itself. __dict__ bypasses the validator, which would copy the tools back."""
        super().build_crew()

        for task in self.crew.tasks:
            task.__dict__["tools"] = []

    def run_crew(self):
        result = super().run_crew()
        self._log_executions(result)
        return result

    @staticmethod
    def _entry_counts(output) -> str:
        profile = getattr(output, "pydantic", None)
        if not profile:
            return f"no structured profile (raw chars: {len(output.raw)})"
        counts = {f: len(getattr(profile, f) or []) for f in ("generic", "tech", "commercial", "team")}
        return f"{counts} total={sum(counts.values())}"

    def _log_executions(self, result):
        """Print the size of each delegated execution next to the manager's final profile."""
        print(f"\n{'-'*80}")
        print(f"  Profiler executions: {len(self.profiler.raw_outputs)}")
        for i, output in enumerate(self.profiler.raw_outputs, 1):
            print(f"    Execution {i}: {len(output)} chars")
        print(f"  Final profile (manager): {self._entry_counts(result)}")
        print(f"{'-'*80}\n")
