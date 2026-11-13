from crewai import Agent, Task, Crew, Process, LLM
from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents.analyst_supervisor import AnalystSupervisor
from due_diligence_mas.crewai_fr.agents.commercial_analyst import CommercialAnalyst_Agent
from due_diligence_mas.crewai_fr.agents.company_profiler import CompanyProfiler_Agent
from due_diligence_mas.crewai_fr.agents.team_analyst import TeamAnalyst_Agent
from due_diligence_mas.crewai_fr.agents.tech_reviewer import TechReviewer_Agent

class AnalystCrew():  
    """
        Crew for managing analyst agents.
        Required agents:
        - Analyst Supervisor
        - Company Profiler
        - Tech Reviewer
        - Commercial Analyst
        - Team Analyst
    """
    
    def __init__(self, args = {}, required_agents: list[str] = []):
        
        self.topic = args
    
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
    
    def build_crew(self):
        """
            Build the crew with the initialized agents and tasks
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
    
    def run_crew(self):
        """
            Run the crew to execute the tasks
        """
        if not hasattr(self, 'crew'):
            self.build_crew()
        
        return self.crew.kickoff()       
    
    def print_crew_info(self):
        print("Crew Agents:")
        for agent in self.crew_agents:
            print(f"- {agent.role}")
        
        print("\nCrew Tasks:")
        for task in self.crew_tasks:
            print(f"- {task.description}")
            
if __name__ == "__main__":
    crew = AnalystCrew(topic="OpenAI", required_agents=[AgentName.TECH_REVIEWER.value])
    crew.print_crew_info()
    
    print("\nRunning the crew...")
    result = crew.run_crew()
    
    print("\nCrew Execution Result:")
    print(f"Tokens Used: {result.token_usage}")
    print(result)