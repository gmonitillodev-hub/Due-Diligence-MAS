from crewai import Agent, Task, Crew, Process, LLM

from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent

class DebateFormatter_Agent(BaseAgent):
    
    def __init__(self):
        
        self.agent_name = AgentName.DEBEATE_FORMATTER.value
        
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
                description=(
                    f"Prepare the debate evidence pack from the following complete analysis: {topic}. "
                    "Condense it into a single structured document: "
                    "a company snapshot, deduplicated evidence items each with a unique ID, source and confidence level, "
                    "a clear separation of facts, assumptions and missing data, and the initial tensions within the analysis. "
                    "Do not add new facts or new analysis."
                ),
                expected_output=(
                    "A structured debate pack with sections: company snapshot, evidence items (ID, statement, source, confidence), "
                    "facts vs assumptions vs missing data, and initial tensions."
                ),
                agent=self.agent,
                context=context
            )
        ]