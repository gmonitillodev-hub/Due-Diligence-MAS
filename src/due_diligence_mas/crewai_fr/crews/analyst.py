from crewai import Agent, Task, Crew, Process
from due_diligence_mas.crewai_fr.utils import is_verbose
from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents.analysts.commercial_analyst import CommercialAnalyst_Agent
from due_diligence_mas.crewai_fr.agents.memo_writer import MemoWriter_Agent
from due_diligence_mas.crewai_fr.agents.analysts.team_analyst import TeamAnalyst_Agent
from due_diligence_mas.crewai_fr.agents.analysts.tech_reviewer import TechReviewer_Agent
from due_diligence_mas.crewai_fr.models import CompanyInput

class AnalystCrew():  
    """
        Crew for managing analyst agents.
        Sequential crew: the specialists run first, then the Memo Writer aggregates their reports.
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
                        
        # Memo writer is the aggregator, so it is always initialized and runs last
        self.memo_writer = MemoWriter_Agent()
        self.crew_agents.append(self.memo_writer.get_agent())

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

        
        if hasattr(self, 'tech_reviewer'):        
            self.tech_reviewer.build_tasks(self.company.topic_for("tech"))
            self.crew_tasks.extend(self.tech_reviewer.get_tasks())
         
        if hasattr(self, 'commercial_analyst'):       
            self.commercial_analyst.build_tasks(self.company.topic_for("commercial"))
            self.crew_tasks.extend(self.commercial_analyst.get_tasks())
        
        if hasattr(self, 'team_analyst'):       
            self.team_analyst.build_tasks(self.company.topic_for("team"))
            self.crew_tasks.extend(self.team_analyst.get_tasks())

        # Aggregation, run by the memo writer on all the specialists' outputs
        specialist_tasks = list(self.crew_tasks)
        self.memo_writer.build_aggregation_tasks(self.company.profile_topic(), context=specialist_tasks)
        self.crew_tasks.extend(self.memo_writer.get_tasks())
    
    def build_crew(self):
        """
            Build the hierarchical crew
        """
        self.crew = Crew(
            name="Analyst Crew",
            agents=self.crew_agents,
            tasks=self.crew_tasks,
            process=Process.sequential,
            tracing=True,
            verbose=is_verbose("crew")
        )
    
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
            

