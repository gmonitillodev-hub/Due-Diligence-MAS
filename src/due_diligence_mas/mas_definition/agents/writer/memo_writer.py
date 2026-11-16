from due_diligence_mas.mas_definition.agents.spec import SpecAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class MemoWriter_Agent(SpecAgent):
    name = AgentName.MEMO_WRITER
    tools = ("current_context",)

    tasks_def = {
        # Aggregation of the specialists' outputs into a single analysis, input of the "memo" task
        "aggregation": TaskDef(
            description="""
                    Aggregate the reports produced by the specialists (technology, commercial, team) in the context
                    into one consolidated analysis, in English.
                    Keep every finding unchanged, with its source, access date and confidence level: do not drop,
                    summarize or generalize anything. Do not add information that is not in the context.
                    Where specialists report conflicting information, keep both versions and state the conflict.
                    {topic}
                """,
            expected_output="""
                    A Markdown analysis report with one section per specialist (Product and Technology,
                    Commercial Analysis, Team and Organization), each containing all of that specialist's findings,
                    followed by:
                    ## Resolved and Unresolved Conflicts
                    ## Missing Information
                    ## Sources
                    Numbered list of all the sources cited by the specialists.
                """,
        ),
        "memo": TaskDef(
            description="""  
                    Write the complete due diligence memo from the following analysis and debate.
                    First call the current context tool to get the user's country, and write the memo in that
                    country's main language (translate the analysis and debate). If the country is unknown, write in English.
                    Translate the text only: keep names, figures, dates, URLs and source titles unchanged.
                    The analysis is the primary source: report it in full and in detail, section by section,
                    keeping every finding with its source, access date and confidence level.
                    Do not drop, merge away or generalize findings to save space: the memo has no length limit.
                    The debate must only be summarized. Do not add information that is not in the input.
                    {topic} 
                """,
            expected_output=""" 
                    A complete due diligence memo, in the language of the user's country (English if unknown), in Markdown, with this structure
                    (translate the section titles into that language):

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
        ),
    }

    def build_tasks(self, topic: str = "", context: list = [], key: str = "memo"):
        super().build_tasks(topic, context, key)
