from typing import Literal, Optional

from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated

Confidence = Literal["verified", "claimed", "tbc"]
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class CompanyInput(BaseModel):
    """Typed target company information provided by the user."""

    company_name: str
    company_site: Optional[str] = None
    company_sector: Optional[str] = None

    def describe(self) -> str:
        parts = [self.company_name]
        if self.company_site:
            parts.append(f"official website: {self.company_site}")
        if self.company_sector:
            parts.append(f"sector: {self.company_sector}")
        return ", ".join(parts)


class Finding(BaseModel):
    """A single source-backed statement."""

    claim: str
    source_url: NonEmptyStr = Field(description="URL of the source supporting the claim")
    access_date: NonEmptyStr = Field(description="ISO date (YYYY-MM-DD) when the source was read")
    confidence: Confidence = Field(
        description="verified = documented evidence, claimed = company/marketing claim, tbc = to be confirmed"
    )


class SpecialistReport(BaseModel):
    """Output contract shared by all specialist agents."""

    agent: str
    summary: NonEmptyStr
    findings: list[Finding] = Field(min_length=1, description="At least one source-backed finding")
    missing: list[str] = Field(default_factory=list, description="Information searched for but not found")


class ConflictResolution(BaseModel):
    topic: str
    candidates: list[Finding]
    chosen: Optional[Finding] = Field(
        default=None, description="Winning finding, or null when the conflict is unresolved (value stays tbc)"
    )
    rationale: str


class SectionStatus(BaseModel):
    agent: str
    valid: bool
    reworked: bool = False
    issues: list[str] = Field(default_factory=list)


class AnalysisReport(BaseModel):
    """Consolidated output of the Analyst Crew, produced by the Analyst Supervisor."""

    company: str
    profile: Optional[SpecialistReport] = None
    tech: Optional[SpecialistReport] = None
    commercial: Optional[SpecialistReport] = None
    team: Optional[SpecialistReport] = None
    conflicts: list[ConflictResolution] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    statuses: list[SectionStatus] = Field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# Analysis report: {self.company}"]
        sections = [
            ("Company profile", self.profile),
            ("Product & technology", self.tech),
            ("Commercial", self.commercial),
            ("Team", self.team),
        ]
        for title, section in sections:
            if section is None:
                continue
            lines += ["", f"## {title}", "", section.summary]
            for f in section.findings:
                lines.append(f"- [{f.confidence}] {f.claim} ({f.source_url}, {f.access_date})")
            if section.missing:
                lines.append("Missing: " + "; ".join(section.missing))
        if self.conflicts:
            lines += ["", "## Resolved conflicts"]
            for c in self.conflicts:
                chosen = c.chosen.claim if c.chosen else "unresolved (tbc)"
                lines.append(f"- {c.topic}: {chosen}. {c.rationale}")
        if self.missing:
            lines += ["", "## Missing information"] + [f"- {m}" for m in self.missing]
        if self.statuses:
            lines += ["", "## Validation status"]
            for s in self.statuses:
                state = "valid" if s.valid else "incomplete"
                note = " (reworked)" if s.reworked else ""
                lines.append(f"- {s.agent}: {state}{note}" + (f" - {'; '.join(s.issues)}" if s.issues else ""))
        return "\n".join(lines)
