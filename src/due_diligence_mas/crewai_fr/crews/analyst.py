from crewai import Agent, Task, Crew, Process
from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents.analysts.analyst_supervisor import AnalystSupervisor
from due_diligence_mas.crewai_fr.agents.analysts.commercial_analyst import CommercialAnalyst_Agent
from due_diligence_mas.crewai_fr.agents.analysts.company_profiler import CompanyProfiler_Agent
from due_diligence_mas.crewai_fr.agents.analysts.team_analyst import TeamAnalyst_Agent
from due_diligence_mas.crewai_fr.agents.analysts.tech_reviewer import TechReviewer_Agent
from due_diligence_mas.crewai_fr.models import CompanyInput

class AnalystCrew():  
    """
        Crew for managing analyst agents.
        The Company Profiler runs first; its report is written into the specialists' task
        text, because in a hierarchical crew the manager would not forward it reliably as
        context. Specialists then run under the Analyst Supervisor (manager).
    """
    
    def __init__(self, args = {}, required_agents: list[str] = []):
        
        self.company = CompanyInput(**args)
        self.topic = self.company.describe()
    
        self.specialists: list = []
        self._initialize_agents(required_agents)

    def _initialize_agents(self, required_agents: list[str]):
        """ 
            Initialize crew agents
        """
        
        self.analyst_supervisor = AnalystSupervisor()
        
        # Profiler is a mandatory agent, so we always initialize it
        self.profiler = CompanyProfiler_Agent()
        
        if AgentName.TECH_REVIEWER.value in required_agents or len(required_agents) == 0:
            self.specialists.append(TechReviewer_Agent())

        if AgentName.COMMERCIAL_ANALYST.value in required_agents or len(required_agents) == 0:        
            self.specialists.append(CommercialAnalyst_Agent())
         
        if AgentName.TEAM_ANALYST.value in required_agents or len(required_agents) == 0:
            self.specialists.append(TeamAnalyst_Agent())

    def _run_profiler(self) -> str:
        self.profiler.build_tasks(self.topic)
        profile_crew = Crew(
            name="Company Profiler Crew",
            agents=[self.profiler.get_agent()],
            tasks=self.profiler.get_tasks(),
            process=Process.sequential,
            tracing=True,
            verbose=True
        )
        return profile_crew.kickoff().raw

    def _build_tasks(self, profile: str):
        """ 
            Build specialists' tasks with the profile embedded in their text
        """
        topic_with_profile = (
            f"{self.topic}\n\nCompany profile produced by the Company Profiler "
            f"(use it as your starting point):\n{profile}"
        )
        
        self.crew_tasks: list[Task] = []
        for specialist in self.specialists:
            specialist.build_tasks(topic_with_profile)
            self.crew_tasks.extend(specialist.get_tasks())

        self.analyst_supervisor.build_tasks(topic_with_profile, context=list(self.crew_tasks))
        self.crew_tasks.extend(self.analyst_supervisor.get_tasks())
    
    def build_crew(self, profile: str):
        """
            Build the hierarchical crew with the specialists and the consolidation task
        """
        self._build_tasks(profile)
        self.crew = Crew(
            name="Analyst Crew",
            agents=[s.get_agent() for s in self.specialists],
            tasks=self.crew_tasks,
            process=Process.hierarchical,
            manager_agent=self.analyst_supervisor.get_agent(),
            tracing=True,
            verbose=True
        )

        # Task.check_tools copies the assigned agent's tools into task.tools, and in a
        # hierarchical crew the manager runs every task: clear them so the manager can
        # only delegate, while each specialist keeps its own tools when it executes.
        # __dict__ bypasses the validator, which would copy the tools back.
        for task in self.crew.tasks:
            task.__dict__["tools"] = []
    
    def run_crew(self) -> str:
        """
            Run the profiler, then the specialists under the supervisor.
            Returns the consolidated analysis in markdown.
        """
        profile = self._run_profiler()
        self.build_crew(profile)
        result = self.crew.kickoff()

        return f"## Company Profile\n\n{profile}\n\n{result.raw}"
    
    def print_crew_info(self):
        print("Crew Agents:")
        for agent in [self.profiler] + self.specialists:
            print(f"- {agent.get_agent().role}")
            
if __name__ == "__main__":
    crew = AnalystCrew(args={"company_name": "OpenAI"}, required_agents=[AgentName.TECH_REVIEWER.value])
    crew.print_crew_info()
    
    print("\nRunning the crew...")
    print(crew.run_crew())
