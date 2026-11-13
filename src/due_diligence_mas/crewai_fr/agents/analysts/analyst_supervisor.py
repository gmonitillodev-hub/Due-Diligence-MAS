
from crewai import Agent, Task, Crew, Process, LLM
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent
from due_diligence_mas.constants.agents_definition import AgentName


class AnalystSupervisor(BaseAgent):

    def __init__(self):
        
        self.agent_name = AgentName.ANALYST_SUPERVISOR.value
                
        self.agent_raw = extract_agent(self.agent_name)
        self.backstory = backstory_builder(self.agent_name)
        self.tasks = []
        
        self.agent = Agent(
            role=self.agent_raw["name"],
            goal=self.agent_raw["goal"],
            backstory=self.backstory,
            llm=LLM_PROVIDER().get_llm(),
            tools=[],
            allow_delegation=False,
            verbose=True,
            max_retry_limit=2
        )
        
    def get_agent(self):
        return self.agent

    def build_tasks(self):
        self.tasks = []

    def get_tasks(self):
        return self.tasks

if __name__ == "__main__":
    agent = AnalystSupervisor()
    print(agent.get_agent())