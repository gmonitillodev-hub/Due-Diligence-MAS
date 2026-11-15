from crewai import Agent, Task, Crew, Process
from due_diligence_mas.crewai_fr.utils import is_verbose
from due_diligence_mas.crewai_fr.agents.analysts.analyst_supervisor import AnalystSupervisor
from due_diligence_mas.crewai_fr.agents.analysts.company_profiler import CompanyProfiler_Agent
from due_diligence_mas.crewai_fr.agents.memo_writer import MemoWriter_Agent

from due_diligence_mas.classes import CompanyInfo

class ProfilerCrew():  
    """
        Crew that profiles the target company (hierarchical, supervisor as manager).
    """
    
    def __init__(self, company_info: CompanyInfo):
        
        self.topic = company_info.describe()
    
        self.crew_agents: list[Agent] = []
        self.crew_tasks: list[Task] = []
            
        self._initialize_agents()    
        self._build_tasks()

    def _initialize_agents(self):
        """ 
            Initialize crew agents
        """
                
        self.supervisor = AnalystSupervisor()
        
        self.profiler = CompanyProfiler_Agent()
        self.crew_agents.append(self.profiler.get_agent())   
        
    def _build_tasks(self):
        """ 
            Build tasks for each agent based on the topic and context
        """
        
        self.profiler.build_tasks(self.topic)
        self.crew_tasks.extend(self.profiler.get_tasks())
            
        """ if hasattr(self, 'supervisor'):        
            self.supervisor.build_tasks(self.topic, context=self.profiler.get_tasks())
            self.crew_tasks.extend(self.supervisor.get_tasks()) """
         
    def build_crew(self):
        """
            Build the crew with the initialized agents and tasks
        """
        self.crew = Crew(
            name="Profiler Crew",
            agents=self.crew_agents,
            tasks=self.crew_tasks,
            process=Process.hierarchical,
            manager_agent=self.supervisor.get_agent(),
            tracing=True,
            verbose=is_verbose("crew")
        )

        # The manager runs every task and would otherwise use the profiler's tools itself;
        # __dict__ bypasses the validator, which would copy the tools back.
        for task in self.crew.tasks:
            task.__dict__["tools"] = []

    def run_crew(self):
        """
            Run the crew to execute the tasks
        """
        if not hasattr(self, 'crew'):
            self.build_crew()
        
        result = self.crew.kickoff()
        self._log_executions(result)
        return result

    @staticmethod
    def _entry_counts(output) -> str:
        profile = getattr(output, "pydantic", None)
        if not profile:
            return f"no structured profile (raw chars: {len(output.raw)})"
        counts = {f: len(getattr(profile, f)) for f in ("generic", "tech", "commercial", "team")}
        return f"{counts} total={sum(counts.values())}"

    def _log_executions(self, result):
        """Print the size of each delegated execution next to the manager's final profile."""
        print(f"\n{'-'*80}")
        print(f"  Profiler executions: {len(self.profiler.raw_outputs)}")
        for i, output in enumerate(self.profiler.raw_outputs, 1):
            print(f"    Execution {i}: {len(output)} chars")
        print(f"  Final profile (manager): {self._entry_counts(result)}")
        print(f"{'-'*80}\n")
    
    def print_crew_info(self):
        print("Crew Agents:")
        for agent in self.crew_agents:
            print(f"- {agent.role}")
        
        print("\nCrew Tasks:")
        for task in self.crew_tasks:
            print(f"- {task.description}")
            
