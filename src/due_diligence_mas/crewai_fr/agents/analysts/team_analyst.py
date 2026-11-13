from crewai import Agent, Task, Crew, Process, LLM

from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent

class TeamAnalyst_Agent(BaseAgent):
    
    def __init__(self):
        
        self.agent_name = AgentName.TEAM_ANALYST.value
        
        self.agent_raw = extract_agent(self.agent_name)
        self.backstory = backstory_builder(self.agent_name)
        
        self.agent = Agent(
            role=self.agent_raw["name"],
            goal=self.agent_raw["goal"],
            backstory=self.backstory,
            llm=LLM_PROVIDER(provider="groq").get_llm(),
            tools=[],
            allow_delegation=False,
            verbose=True,
            max_retry_limit=2
        )
    
    def get_agent(self):
        return self.agent
    
    def get_tasks(self):
        return self.tasks

    def build_tasks(self, topic: str = "", context: list = []):
        self.tasks = [
            Task(
                description=f"Review the team dynamics and performance of the target company in the {topic} sector",
                expected_output="A detailed review of the team dynamics and performance of the target company",
                agent=self.agent,
                context=context
            )
        ]