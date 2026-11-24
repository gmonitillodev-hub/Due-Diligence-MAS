from due_diligence_mas.mas_definition.agents.dd_agent import DDAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class MemoWriter_Agent(DDAgent):
    name = AgentName.MEMO_WRITER
    tools = ("current_context",)

    tasks_def = {
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
                    Write the due diligence memo from the analysis and the debate below.
                    First call the current context tool: it returns the user's country and the current date and time.
                    - Language: write the whole memo, section titles included, in the main language of that country
                      (the tool gives the country code). If the country is unknown, write in English.
                      Translate the text only: names, figures, URLs and source titles stay unchanged.
                    - Dates: the current date from the tool is "today". Use it for the memo date and for every
                      relative reference ("as of today", "X months ago", "recent", "upcoming"), by comparing the
                      dates of the sources with it. Never assume a different date.
                    The analysis is the primary source: carry all of its findings into the memo, with their figures,
                    names, dates, sources and confidence level, and do not shorten them to save space (no length limit).
                    The debate is only summarized. Add nothing that is not in the input.
                    {topic}
                """,
            expected_output="""
                    A due diligence memo in Markdown, written as a flowing narrative that a person reads from top to bottom:
                    connected paragraphs that explain the findings and how they relate, not a list of bullet points.
                    Use tables only where they make data clearer (offering, customers, competitors, team members, risks).
                    The language and the date follow the current context, as described in the task.

                    Open with the title "Due Diligence Memo — [Company]", today's date and a line on the scope
                    (areas reviewed, evidence cutoff, exclusions). Then cover, in the order that reads best:
                    - an executive summary (about 250 words): the business, the material findings, the preliminary conclusion;
                    - the company profile, the product and technology, the commercial picture and the team, each in
                      depth and with the sources cited inline as [1], [2]; add a section for any other topic the
                      analysis covers;
                    - a short summary of the debate (PRO case, CONTRO case, the judge's conclusion), or a note that
                      the debate was not performed;
                    - the material risks, with evidence, potential impact and the follow-up needed;
                    - the information gaps and limits of the evidence, with the priority questions;
                    - the preliminary conclusion and next steps: whether the evidence supports going on, going on
                      under conditions, or pausing, and why;
                    - the numbered list of sources, with title, URL and publication or access date.

                    Along the way:
                    - say whether each statement is verified, a company claim, an estimate or still to be confirmed,
                      in the flow of the text and not as a label on every line;
                    - never invent facts or references; say when data is not available;
                    - missing evidence does not prove that a risk does not exist;
                    - keep allegations apart from established findings.
                """,
        ),
    }

    def build_tasks(self, topic: str = "", context: list = [], key: str = "memo"):
        super().build_tasks(topic, context, key)
