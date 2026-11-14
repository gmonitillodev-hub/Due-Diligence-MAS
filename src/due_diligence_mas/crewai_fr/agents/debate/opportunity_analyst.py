from crewai import Agent, Task, Crew, Process, LLM

from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent, agent_limits

class OpportunityAnalyst_Agent(BaseAgent):
    
    def __init__(self):
        
        self.agent_name = AgentName.OPPORTUNITY_ANALYST.value
        
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
            max_retry_limit=2,
            **agent_limits(self.agent_name)
        )
    
    def get_agent(self):
        return self.agent
    
    def get_tasks(self):
        return self.tasks

    def build_tasks(self, topic: str = "", context: list = []):
        self.tasks = [
            Task(
                description=(
                    "Build the PRO case for the target company. "
                    "Using only the formatted debate document received from the previous task, identify the strongest evidence-backed reasons to continue diligence or invest: "
                    "positive signals, market timing, commercial upside, product strengths, technical defensibility, founder-market fit and traction. "
                    "Reference evidence IDs for every argument, flag arguments resting on weak evidence, do not invent facts or search externally, "
                    "and do not ignore missing data."
                ),
                expected_output=(
                    "A structured PRO case: ranked strengths and reasons to continue diligence, each linked to evidence IDs "
                    "with an evidence-strength note."
                ),
                agent=self.agent,
                context=context
            )
        ]