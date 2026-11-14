from crewai import Agent, Task, Crew, Process, LLM

from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
from due_diligence_mas.crewai_fr.tools.file_generator import generate_memo_file
from due_diligence_mas.crewai_fr.utils import backstory_builder, extract_agent

class MemoWriter_Agent(BaseAgent):
    
    def __init__(self):
        
        self.agent_name = AgentName.MEMO_WRITER.value
        
        self.agent_raw = extract_agent(self.agent_name)
        self.backstory = backstory_builder(self.agent_name)
        
        self.agent = Agent(
            role=self.agent_raw["name"],
            goal=self.agent_raw["goal"],
            backstory=self.backstory,
            llm=LLM_PROVIDER().get_llm(),
            tools=[generate_memo_file],
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
                description=f""" 
                    Considering the following analysis and debate, create a structured memo. 
                    Do not add extra informations and use all data from as input.
                    
                    After the creation generate the markdown file using available tools.
                    {topic} 
                """,
                expected_output = """
                    A due diligence memo in Markdown, up to 700 words
                    excluding sources, using the following structure:

                    # Due Diligence Memo — [Company]
                    Date: [date] | Purpose: [decision being supported]
                    Scope: [areas reviewed, evidence cutoff date, and exclusions]

                    ## Executive Summary
                    Summarize the business, material findings, and preliminary conclusion.

                    ## Key Findings
                    Cover business model, ownership and management, market position,
                    financial performance, technology and operations, and legal or
                    reputational issues, where relevant and supported by evidence.
                    State the period and currency for financial figures.

                    ## Material Risks
                    Provide a short table:
                    Risk | Supporting evidence | Potential impact | Required follow-up

                    Prioritize material risks and explain their significance.
                    Distinguish allegations from established findings.

                    ## Information Gaps and Limitations
                    Identify missing or conflicting information, unverified assumptions,
                    and priority documents or management questions.

                    ## Preliminary Conclusion and Next Steps
                    State whether the evidence supports further evaluation, conditional
                    progress, or a pause pending verification. Explain the rationale
                    and any conditions. If evidence is insufficient, say so explicitly.

                    ## Sources
                    List numbered sources with title, URL, and publication date where available.

                    Requirements:
                    - Cite material factual claims inline using [1], [2], etc.
                    - Distinguish verified facts, company claims, estimates, and analysis.
                    - Never invent facts or references; mark missing data as "Not available".
                    - Do not treat missing evidence as proof that no risk exists.
                    - Keep findings decision-focused and avoid repetitive background.
                    - Add extra section if needed based on input analysis.
                """,
                agent=self.agent,
                context=context
            )
        ]