from crewai import Agent, Task, Crew, Process, LLM
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.models import SpecialistReport
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.tools.tavily import get_tavily_tool
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent
from due_diligence_mas.constants.agents_definition import AgentName

class CompanyProfiler_Agent(BaseAgent):
    
    def __init__(self):
        self.agent_name = AgentName.COMPANY_PROFILER.value
        self.agent_raw = extract_agent(self.agent_name)
        self.backstory = backstory_builder(self.agent_name)
        
        self.agent = Agent(
            role=self.agent_raw["name"],
            goal=self.agent_raw["goal"],
            backstory=self.backstory,
            llm=LLM_PROVIDER().get_llm(),
            tools=[get_tavily_tool("profile_search"), get_tavily_tool("page_extractor")],
            allow_delegation=False,
            verbose=True,
            max_retry_limit=2
        )
        
    def get_agent(self):
        return self.agent
    
    def build_tasks(self, topic: str = "", context: list = []):
        self.tasks = [
            Task(
                description=f"Profile the following target company: {topic}. Extract all possible informations throug websites using also sitemaps to get all relevant pages.",
                expected_output=(
                    "Return a SpecialistReport: agent name, a short summary, findings (each with claim, source_url, access_date in YYYY-MM-DD and confidence verified/claimed/tbc) and the list of missing information. Include the official GitHub organization, LinkedIn and team page URLs among the findings when found."
                ),
                agent=self.agent,
                output_pydantic=SpecialistReport,
                context=context
            )
        ]
                
    def get_tasks(self):
        return self.tasks