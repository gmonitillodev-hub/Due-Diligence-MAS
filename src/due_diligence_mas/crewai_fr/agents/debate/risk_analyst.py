from crewai import Agent, Task, Crew, Process, LLM

from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent

class RiskAnalyst_Agent(BaseAgent):
    
    def __init__(self):
        
        self.agent_name = AgentName.RISK_ANALYST.value
        
        self.agent_raw = extract_agent(self.agent_name)
        self.backstory = backstory_builder(self.agent_name)
        
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
    
    def get_tasks(self):
        return self.tasks

    def build_tasks(self, topic: str = "", context: list = []):
        self.tasks = [
            Task(
                description=(
                    "Build the CONTRO case for the target company. "
                    "Using the formatted debate document and the PRO arguments received from the previous tasks, challenge weak or unsupported PRO claims and surface "
                    "commercial, market, product/technical, team and financial risks, critical missing evidence and possible deal breakers. "
                    "Reference evidence IDs or explicitly cite missing data for every argument; be rigorous, not merely pessimistic."
                ),
                expected_output=(
                    "A structured CONTRO case: rebuttals to PRO arguments, ranked risks and deal breakers, and critical missing data, "
                    "each linked to evidence IDs."
                ),
                agent=self.agent,
                context=context
            )
        ]