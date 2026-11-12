from crewai import Agent, Task, Crew, Process, LLM
from due_diligence_mas.crewai_fr.agents.analyst_supervisor import AnalystSupervisor
from due_diligence_mas.crewai_fr.agents.commercial_analyst import CommercialAnalyst_Agent
from due_diligence_mas.crewai_fr.agents.company_profiler import CompanyProfiler_Agent
from due_diligence_mas.crewai_fr.agents.team_analyst import TeamAnalyst_Agent
from due_diligence_mas.crewai_fr.agents.tech_reviewer import TechReviewer_Agent

class AnalystCrew():
    
    def __init__(self, topic: str = "technology"):
        
        self.crew_agents: list[Agent] = []
        self.crew_tasks: list[Task] = []
        
        # Initialize the Analyst Supervisor Agent
        analyst_supervisor_agent = AnalystSupervisor()
        self.crew_agents.append(analyst_supervisor_agent.get_agent())

        
        # Initialize crew agents      
        profiler = CompanyProfiler_Agent()
        self.crew_agents.append(profiler.get_agent())

        tech_reviewer = TechReviewer_Agent()
        self.crew_agents.append(tech_reviewer.get_agent())

        commercial_analyst = CommercialAnalyst_Agent()
        self.crew_agents.append(commercial_analyst.get_agent())
        
        team_analyst = TeamAnalyst_Agent()
        self.crew_agents.append(team_analyst.get_agent())

        # Build tasks for each agent based on the topic and context
        profiler.build_tasks(topic)
        
        tr_context = profiler.get_tasks()
        tech_reviewer.build_tasks(topic, context=tr_context)
        
        ca_context = profiler.get_tasks() 
        commercial_analyst.build_tasks(topic, context=ca_context)
        
        ta_context = profiler.get_tasks()
        team_analyst.build_tasks(topic, context=ta_context)

        self.crew_tasks.extend(profiler.get_tasks() + tech_reviewer.get_tasks() + commercial_analyst.get_tasks() + team_analyst.get_tasks())

    def _bind_tasks_context(self):
        pass
        
    def print_crew_info(self):
        print("Crew Agents:")
        for agent in self.crew_agents:
            print(f"- {agent.role}")
        
        print("\nCrew Tasks:")
        for task in self.crew_tasks:
            print(f"- {task.description}")
            
if __name__ == "__main__":
    crew = AnalystCrew(topic="technology")
    crew.print_crew_info()