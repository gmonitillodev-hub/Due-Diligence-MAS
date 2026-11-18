from due_diligence_mas.mas_definition.classes.company import AnalysisReview, CompanyProfile, ProfiledCompany, ProfileReview
from typing import Annotated, Optional
import operator
from pydantic import BaseModel, Field


def merge_profile(old: Optional[CompanyProfile], new: Optional[CompanyProfile]) -> Optional[CompanyProfile]:
    """Reducer: overwrite only the profile fields explicitly set by the node, keep the others."""
    if old is None or new is None:
        return new if old is None else old
    return old.model_copy(update={k: getattr(new, k) for k in new.model_fields_set})


class SupervisionState(BaseModel):
    """Control data of the supervisor: profile gate and analysis completeness gate."""

    profile_review: Optional[ProfileReview] = None
    profile_revisions: int = 0
    profile_validated: bool = False
    # Issues already sent to the profiler: each issue is addressed only once, the supervisor reports only new ones
    requested_issues: list[str] = Field(default_factory=list)
    analysis_review: Optional[AnalysisReview] = None


def merge_supervision(old: SupervisionState, new: SupervisionState) -> SupervisionState:
    """Reducer: overwrite only the fields explicitly set by the node; requested_issues accumulates."""
    update = {k: getattr(new, k) for k in new.model_fields_set}
    if "requested_issues" in update:
        update["requested_issues"] = old.requested_issues + update["requested_issues"]
    return old.model_copy(update=update)


class DueDiligence_State(ProfiledCompany):

    # --- Profiling (company_info and company_profile come from ProfiledCompany) ---
    company_profile: Annotated[Optional[CompanyProfile], merge_profile] = None
    # Raw output of every profiler run, merged by the supervisor so no information is lost between iterations
    profile_iterations: Annotated[list[CompanyProfile], operator.add] = Field(default_factory=list)

    # --- Supervision ---
    supervision: Annotated[SupervisionState, merge_supervision] = Field(default_factory=SupervisionState)

    # --- Analysis and debate ---
    analysis_results: Optional[str] = None
    human_decision: Optional[str] = None
    debate_pack: Optional[str] = None
    pro_case: Optional[str] = None
    contro_case: Optional[str] = None
    debate_results: Optional[str] = None

    # --- Output ---
    final_report: Optional[str] = None

    messages: Annotated[list, operator.add] = Field(default_factory=list)
