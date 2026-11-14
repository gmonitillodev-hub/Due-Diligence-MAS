from crewai import Agent, Task, Crew, Process, LLM
from crewai.agents.parser import AgentFinish
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.tools.request_handler import get_current_context
from due_diligence_mas.crewai_fr.tools.tavily import get_tavily_tool
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent, agent_limits, is_verbose
from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.models import CompanyProfile

class CompanyProfiler_Agent(BaseAgent):
    
    def __init__(self):
        self.agent_name = AgentName.COMPANY_PROFILER.value
        self.agent_raw = extract_agent(self.agent_name)
        self.backstory = backstory_builder(self.agent_name)
        # Raw final output of every execution delegated to this agent, in order
        self.raw_outputs: list[str] = []
        
        self.agent = Agent(
            role=self.agent_raw["name"],
            goal=self.agent_raw["goal"],
            backstory=self.backstory,
            llm=LLM_PROVIDER().get_llm(),
            tools=[get_tavily_tool("profile_search"), get_tavily_tool("page_extractor"), get_current_context],
            allow_delegation=False,
            verbose=is_verbose("agent"),
            max_retry_limit=2,
            step_callback=self._collect_raw_output,
            **agent_limits(self.agent_name)
        )

    def _collect_raw_output(self, step):
        # The callback also receives tool results: keep only the final answers
        if isinstance(step, AgentFinish):
            self.raw_outputs.append(step.text)
            print(f"\n  [Profiler] execution {len(self.raw_outputs)} finished ({len(step.text)} chars)\n")
        
    def get_agent(self):
        return self.agent
    
    def build_tasks(self, topic: str = "", context: list = []):
        self.tasks = [
            Task(
                description=(
                    f"Profile the following target company: {topic}. Extract all possible informations through websites, using also sitemaps to get all relevant pages. "
                    "Always try the company's pages that usually hold key facts (about, team, company, careers, contact, footer links to GitHub and LinkedIn) before concluding that an item is missing. "
                    "If the work is delegated more than once, the final answer must cumulate the facts of ALL the executions, "
                    "in particular the earliest ones: never report only the result of the last execution, and never drop an entry already collected. "
                    "If a follow-up request lists items already found, do not repeat them: search only the missing ones, "
                    "and report each item you still cannot find as 'missing (not found after search)'."
                ),
                expected_output=(
                    "English, no markdown, in four fields: generic, tech, commercial, team. Each field is a list with one entry per fact or gap. "
                    "Be exhaustive: include every fact collected, without summarizing or merging entries; there is no length limit. "
                    "Every fact entry has the form: fact | source URL | access date (YYYY-MM-DD) | verified, claimed or to be confirmed. The source must be a URL, never only a publication name.\n"
                    "generic: official website, what the company does, sector, headquarters, founding year, "
                    "products or services, value proposition, target customers, clients/partners/case studies, geography.\n"
                    "tech (for technology review): official GitHub organization URL (only if linked from the company site or docs), "
                    "documentation/API/pricing/product page URLs, technology claims found, and what is still missing.\n"
                    "commercial (for commercial analysis): clients, pricing, market and traction signals, funding or press mentions found, "
                    "and what is still missing.\n"
                    "team (for team analysis): team page URL, LinkedIn company page URL, names and roles of visible team members, "
                    "and what is still missing."
                ),
                agent=self.agent,
                output_pydantic=CompanyProfile,
                context=context
            )
        ]
                
    def get_tasks(self):
        return self.tasks