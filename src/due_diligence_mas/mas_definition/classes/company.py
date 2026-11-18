from typing import Optional
from pydantic import BaseModel, Field

class CompanyInfo(BaseModel):
    """Target company information provided by the user."""

    company_name: Optional[str] = None
    company_site: Optional[str] = None
    company_sector: Optional[str] = None
    additional_info: Optional[str] = None

    def describe(self) -> str:
        parts = [self.company_name or "Unknown company"]
        if self.company_site:
            parts.append(f"official website: {self.company_site}")
        if self.company_sector:
            parts.append(f"sector: {self.company_sector}")
        if self.additional_info:
            parts.append(f"additional information: {self.additional_info}")
        return ", ".join(parts)


class CompanyProfile(BaseModel):
    """Profiling output: shared facts plus one list of entries per specialist."""

    generic: Optional[list[str]] = Field(default=None, description="Generic company info, one entry per fact: fact | source URL | access date | status")
    tech: Optional[list[str]] = Field(default=None, description="Inputs and gaps for technology review, one entry per fact or gap")
    commercial: Optional[list[str]] = Field(default=None, description="Inputs and gaps for commercial analysis, one entry per fact or gap")
    team: Optional[list[str]] = Field(default=None, description="Inputs and gaps for team analysis, one entry per fact or gap")

    def for_specialist(self, specialist: str) -> str:
        """Generic info plus the entries of the given specialist: tech, commercial or team."""
        generic = "\n".join(f"- {e}" for e in self.generic or [])
        own = "\n".join(f"- {e}" for e in getattr(self, specialist) or [])
        return f"GENERIC INFO:\n{generic}\n\n{specialist.upper()} INPUTS:\n{own}"


class ProfileReview(BaseModel):
    """Supervisor verdict on the company profile."""

    approved: bool = Field(description="True only if the profile is complete, source-backed and usable by the specialists")
    issues: list[str] = Field(default_factory=list, description="Concrete problems found: missing fields, facts without source URL, unsupported claims, gaps not declared")
    feedback: str = Field(default="", description="Actionable instructions for the profiler to fix the issues; empty if approved")


class AnalysisReview(BaseModel):
    """Supervisor completeness verdict on the analysts' results."""

    score: int = Field(ge=0, le=10, description="Single overall completeness score of all the analyses together, from 0 (nothing usable) to 10 (fully complete)")
    missing: list[str] = Field(description="Concrete missing topics, unsupported claims or undeclared gaps; empty if none")
    summary: str = Field(description="Short motivation of the score")


class ProfiledCompany(BaseModel):
    """Target company info together with the profile produced by the profiling crew."""

    company_info: Optional[CompanyInfo] = None
    company_profile: Optional[CompanyProfile] = None

    def describe(self) -> str:
        return self.company_info.describe()

    def profile_topic(self) -> str:
        """Company description plus the generic info from the profiling crew."""
        generic = "\n".join(f"- {e}" for e in self.company_profile.generic or []) if self.company_profile else ""
        return f"{self.describe()}\n\nCOMPANY PROFILE:\n{generic}"

    def topic_for(self, specialist: str) -> str:
        """Company description plus generic info and the entries of the given specialist: tech, commercial or team."""
        if not self.company_profile:
            return self.describe()
        return f"{self.describe()}\n\n{self.company_profile.for_specialist(specialist)}"
