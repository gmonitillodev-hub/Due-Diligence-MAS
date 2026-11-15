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

    generic: list[str] = Field(description="Generic company info, one entry per fact: fact | source URL | access date | status")
    tech: list[str] = Field(description="Inputs and gaps for technology review, one entry per fact or gap")
    commercial: list[str] = Field(description="Inputs and gaps for commercial analysis, one entry per fact or gap")
    team: list[str] = Field(description="Inputs and gaps for team analysis, one entry per fact or gap")

    def for_specialist(self, specialist: str) -> str:
        """Generic info plus the entries of the given specialist: tech, commercial or team."""
        generic = "\n".join(f"- {e}" for e in self.generic)
        own = "\n".join(f"- {e}" for e in getattr(self, specialist))
        return f"GENERIC INFO:\n{generic}\n\n{specialist.upper()} INPUTS:\n{own}"


class ProfiledCompany(BaseModel):
    """Target company info together with the profile produced by the profiling crew."""

    company_info: CompanyInfo
    company_profile: Optional[CompanyProfile] = None

    def describe(self) -> str:
        return self.company_info.describe()

    def profile_topic(self) -> str:
        """Company description plus the generic info from the profiling crew."""
        generic = "\n".join(f"- {e}" for e in self.company_profile.generic) if self.company_profile else ""
        return f"{self.describe()}\n\nCOMPANY PROFILE:\n{generic}"

    def topic_for(self, specialist: str) -> str:
        """Company description plus generic info and the entries of the given specialist: tech, commercial or team."""
        if not self.company_profile:
            return self.describe()
        return f"{self.describe()}\n\n{self.company_profile.for_specialist(specialist)}"
