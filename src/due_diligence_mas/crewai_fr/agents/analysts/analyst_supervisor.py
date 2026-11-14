
from crewai import Agent, Task, Crew, Process, LLM
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.models import AnalysisReport
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
            allow_delegation=True,
            verbose=True,
            max_retry_limit=2
        )
        
    def get_agent(self):
        return self.agent

    def build_tasks(self, topic: str = "", context: list = []):
        # In a hierarchical crew the manager runs every task, so no agent is bound here
        self.tasks = [
            Task(
                description=(
                    f"Consolidate the outputs of all specialists for the target company: {topic}. "
                    "Do not run searches or use research tools: delegate any missing work to the owning specialist. "
                    "Place each specialist report in its own section without rewriting its findings. "
                    "Where specialists report conflicting information, decide which finding prevails "
                    "(primary over secondary source, more recent over older, verified over claimed over tbc) "
                    "and record the decision in conflicts with a rationale; if undecidable, leave chosen empty "
                    "and treat the value as tbc. List in missing everything that remains unknown."
                ),
                expected_output=(
                    "An AnalysisReport with the company name, one section per specialist "
                    "(profile, tech, commercial, team), resolved conflicts and the missing information."
                ),
                output_pydantic=AnalysisReport,
                context=context,
            )
        ]

    def get_tasks(self):
        return self.tasks

if __name__ == "__main__":
    agent = AnalystSupervisor()
    print(agent.get_agent())