from crewai import Agent, Task, Crew, Process, LLM
from due_diligence_mas.crew.agents import BaseAgent
from due_diligence_mas.crew.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crew.utils import backstory_builder, extract_agent
from due_diligence_mas.constants.agents_definition import AgentName

class CompanyProfiler_Agent(BaseAgent):
    def __init__(self):
        self.agent_name = AgentName.COMPANY_PROFILER.value
        self.agent_raw = extract_agent(self.agent_name)
        self.backstory = backstory_builder(self.agent_name)
        
        self.agent = Agent(
            role=self.agent_raw["role"],
            goal=self.agent_raw["goal"],
            backstory=self.backstory,
            llm=LLM_PROVIDER(provider="groq").get_llm(),
            allow_delegation=False,
            verbose=True
        )
        
    def get_agent(self):
        return self.agent
    
    def build_tasks(self):
        self.tasks = []
        
    def get_tasks(self):
        return self.tasks