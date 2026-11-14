from typing import Optional

from pydantic import BaseModel, Field


class CompanyInput(BaseModel):
    """Typed target company information provided by the user."""

    company_name: str
    company_site: Optional[str] = None
    company_sector: Optional[str] = None
    general_info: list[str] = Field(default_factory=list)
    tech_specs: list[str] = Field(default_factory=list)
    commercial_specs: list[str] = Field(default_factory=list)
    team_specs: list[str] = Field(default_factory=list)

    def describe(self) -> str:
        parts = [self.company_name]
        if self.company_site:
            parts.append(f"official website: {self.company_site}")
        if self.company_sector:
            parts.append(f"sector: {self.company_sector}")
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
