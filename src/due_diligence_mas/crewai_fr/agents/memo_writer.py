from crewai import Agent, Task, Crew, Process, LLM

from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.agents import BaseAgent
from due_diligence_mas.crewai_fr.agents.classes.llm_provider import LLM_PROVIDER
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
                description=f""" 
                    Write the complete due diligence memo, in English, from the following analysis and debate.
                    The analysis is the primary source: report it in full and in detail, section by section,
                    keeping every finding with its source, access date and confidence level.
                    Do not drop, merge away or generalize findings to save space: the memo has no length limit.
                    The debate must only be summarized. Do not add information that is not in the input.
                    {topic} 
                """,
                expected_output = """
                    A complete due diligence memo in English, in Markdown, with this structure:

                    # Due Diligence Memo — [Company]
                    Date: [date] | Scope: [areas reviewed, evidence cutoff date, exclusions]

                    ## Executive Summary
                    Business, material findings and preliminary conclusion (max 250 words).

                    ## Company Profile
                    ## Product and Technology
                    ## Commercial Analysis
                    ## Team and Organization
                    For each section report ALL the findings of the corresponding analysis, in detail,
                    with figures, names, dates and periods/currencies, and cite them inline as [1], [2], etc.
                    Use tables where they preserve information (offering, customers, competitors, team members).
                    Tag each statement as verified, company claim, estimate or to be confirmed.
                    Add other sections if the analysis contains topics not covered above.

                    ## Debate Summary
                    A short synthesis of the PRO case, the CONTRO case and the Judge's conclusion,
                    or "Debate not performed".

                    ## Material Risks
                    Table: Risk | Supporting evidence | Potential impact | Required follow-up

                    ## Information Gaps and Limitations
                    Missing or conflicting information, unverified assumptions, priority questions.

                    ## Preliminary Conclusion and Next Steps
                    Whether the evidence supports further evaluation, conditional progress or a pause,
                    with rationale and conditions. If the evidence is insufficient, say so explicitly.

                    ## Sources
                    Numbered list with title, URL and publication/access date.

                    Requirements:
                    - Completeness first: every finding of the analysis must appear in the memo.
                    - Never invent facts or references; mark missing data as "Not available".
                    - Do not treat missing evidence as proof that no risk exists.
                    - Distinguish allegations from established findings.
                """,
                agent=self.agent,
                context=context
            )
        ]