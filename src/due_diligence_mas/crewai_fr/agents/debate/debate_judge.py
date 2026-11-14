from crewai import Agent, Task, Crew, Process, LLM

from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent, agent_limits

class DebateJudge_Agent(BaseAgent):
    
    def __init__(self):
        
        self.agent_name = AgentName.DEBATE_JUDGE.value
        
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
                    "Judge the PRO/CONTRO debate on the target company, using the PRO and CONTRO cases received from the previous tasks. "
                    "Weigh the strength of the PRO arguments against the severity of the CONTRO arguments, assess evidence quality, "
                    "flag unsupported claims and critical missing data, decide whether risks are knowable, mitigable or deal-breaking, "
                    "identify the central investment tension and whether further diligence is justified. "
                    "Do not write the final memo."
                ),
                expected_output=(
                    "A balanced preliminary judgement (SWOT analysis): evidence-quality assessment of both sides, central tension, "
                    "risk classification, and a recommendation on further diligence, for the Memo Writer to use."
                ),
                agent=self.agent,
                context=context
            )
        ]