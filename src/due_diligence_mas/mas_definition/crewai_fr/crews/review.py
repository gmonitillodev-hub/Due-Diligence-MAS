from due_diligence_mas.mas_definition.agents.analysts.analysis_reviewer import AnalysisReviewer_Agent
from due_diligence_mas.mas_definition.classes import ProfiledCompany
from due_diligence_mas.mas_definition.classes.company import AnalysisReview
from due_diligence_mas.mas_definition.crewai_fr.crews.base import BaseCrew


class AnalysisReviewCrew(BaseCrew):
    """
    Crew that scores the completeness of the aggregated analysis; the reviewer may create follow-up tasks through the task manager MCP tools.
    """

    name = "Analysis Review Crew"

    def __init__(self, company: ProfiledCompany, analysis: str):
        generic = "\n".join(company.company_profile.generic or []) if company.company_profile else ""
        self.topic = f"COMPANY: {company.company_info.describe()}\n\nPROFILE:\n{generic}\n\nAGGREGATED ANALYSIS:\n{analysis}"
        super().__init__()

    def _setup(self):
        self.reviewer = self.add(AnalysisReviewer_Agent(), self.topic, key="review")

    def run_crew(self) -> AnalysisReview:
        """Returns the structured review."""
        return super().run_crew().pydantic
