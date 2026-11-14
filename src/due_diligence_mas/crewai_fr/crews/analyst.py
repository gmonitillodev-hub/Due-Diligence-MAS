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
        Hierarchical crew: the Analyst Supervisor is the manager, the Company Profiler and
        the specialists are its workers.
    """
    
    def __init__(self, args = {}, required_agents: list[str] = []):
        
        self.company = CompanyInput(**args)
        self.topic = self.company.describe()
    
        self.crew_agents: list[Agent] = []
        self.crew_tasks: list[Task] = []
            
        self._initialize_agents(required_agents)    
        self._build_tasks()

    def _initialize_agents(self, required_agents: list[str]):
        """ 
            Initialize crew agents
        """
        
        self.analyst_supervisor = AnalystSupervisor()
        
        # Profiler is a mandatory agent, so we always initialize it
        self.profiler = CompanyProfiler_Agent()
        self.crew_agents.append(self.profiler.get_agent())
        
        if AgentName.TECH_REVIEWER.value in required_agents or len(required_agents) == 0:
            self.tech_reviewer = TechReviewer_Agent()
            self.crew_agents.append(self.tech_reviewer.get_agent())

        if AgentName.COMMERCIAL_ANALYST.value in required_agents or len(required_agents) == 0:        
            self.commercial_analyst = CommercialAnalyst_Agent()
            self.crew_agents.append(self.commercial_analyst.get_agent())
         
        if AgentName.TEAM_ANALYST.value in required_agents or len(required_agents) == 0:
            self.team_analyst = TeamAnalyst_Agent()
            self.crew_agents.append(self.team_analyst.get_agent())

    def _build_tasks(self):
        """ 
            Build tasks for each agent based on the topic and context
        """
        self.profiler.build_tasks(self.topic)
        self.crew_tasks.extend(self.profiler.get_tasks())
        
        if hasattr(self, 'tech_reviewer'):        
            tr_context = self.profiler.get_tasks()
            self.tech_reviewer.build_tasks(self.topic, context=tr_context)
            self.crew_tasks.extend(self.tech_reviewer.get_tasks())
         
        if hasattr(self, 'commercial_analyst'):       
            ca_context = self.profiler.get_tasks() 
            self.commercial_analyst.build_tasks(self.topic, context=ca_context)
            self.crew_tasks.extend(self.commercial_analyst.get_tasks())
        
        if hasattr(self, 'team_analyst'):       
            ta_context = self.profiler.get_tasks()
            self.team_analyst.build_tasks(self.topic, context=ta_context)
            self.crew_tasks.extend(self.team_analyst.get_tasks())

        # Final consolidation, run by the supervisor (manager) on all outputs
        self.analyst_supervisor.build_tasks(self.topic, context=list(self.crew_tasks))
        self.crew_tasks.extend(self.analyst_supervisor.get_tasks())
    
    def build_crew(self):
        """
            Build the hierarchical crew
        """
        self.crew = Crew(
            name="Analyst Crew",
            agents=self.crew_agents,
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
            Run the crew. Returns the consolidated analysis in markdown.
        """
        if not hasattr(self, 'crew'):
            self.build_crew()

        return self.crew.kickoff().raw
    
    def print_crew_info(self):
        print("Crew Agents:")
        for agent in self.crew_agents:
            print(f"- {agent.role}")
            
if __name__ == "__main__":
    crew = AnalystCrew(args={"company_name": "OpenAI"}, required_agents=[AgentName.TECH_REVIEWER.value])
    crew.print_crew_info()
    
    print("\nRunning the crew...")
    print(crew.run_crew())
