from crewai import Agent, Task, Crew, Process, LLM

from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.tools.tavily import get_tavily_tool
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent, agent_limits

class CommercialAnalyst_Agent(BaseAgent):
    
    def __init__(self):
        
        self.agent_name = AgentName.COMMERCIAL_ANALYST.value
        
        self.agent_raw = extract_agent(self.agent_name)
        self.backstory = backstory_builder(self.agent_name)
        
        self.agent = Agent(
            role=self.agent_raw["name"],
            goal=self.agent_raw["goal"],
            backstory=self.backstory,
            llm=LLM_PROVIDER().get_llm(),
            tools=[get_tavily_tool("search"), get_tavily_tool("funding_search"), get_tavily_tool("page_extractor")],
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
                    f"Review the commercial aspects of the target company: {topic}. "
                    "Start from the provided context (official URLs, findings, missing items): search only for information that is absent or listed as missing, and do not repeat searches already covered by the context. "
                    "Cover market, competitors, pricing, revenue model, go-to-market, traction and public funding. "
                    "Stay within commercial topics: product/technology and team belong to other specialists."
                ),
                expected_output=(
                    "A markdown report with: a short summary; the findings as a list, each with its source URL, access date and whether it is verified, a company claim or to be confirmed; and a 'Missing information' list."
                ),
                agent=self.agent,
                context=context
            )
        ]