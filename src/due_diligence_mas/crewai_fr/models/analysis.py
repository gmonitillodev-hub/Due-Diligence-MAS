from typing import Optional

from pydantic import BaseModel


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
