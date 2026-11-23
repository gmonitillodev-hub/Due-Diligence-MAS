from due_diligence_mas.mas_definition.agents.spec import SpecAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.research import CONTEXT_FIRST

FINANCIAL_SOURCES = [
    "Companies House, UK annual accounts (https://find-and-update.company-information.service.gov.uk/): open the company, Filing history > Accounts, and the PDF of the relevant period. "
    "Record turnover, profit or loss, balance sheet, the financial year-end and whether the accounts cover the company or the group; small filings may omit the income statement.",
    "DATA INPI, French annual accounts (https://data.inpi.fr/recherche_avancee/entreprises): search by nine-digit Siren, or by name and location, then 'Documents associés' > 'comptes annuels'. "
    "Documents need a free account: if not authenticated, record the company record URL and flag the accounts for manual retrieval.",
    "Tech.eu Funding Explorer, European rounds (https://funding.tech.eu/companies): open the matching profile, confirm country and website, and capture date, stage, amount, investors and cited source of each round. "
    "Keep equity, debt and grants distinct and verify the original currency in the cited announcement.",
    "SEC EDGAR, U.S. private offerings (https://www.sec.gov/edgar/search/): search the issuer's legal name or CIK, forms D and D/A, section 13 'Offering and Sales Amounts' ('Total Amount Sold', filing date). "
    "Use the latest amendment of an offering and never count original and amended filings as separate rounds.",
    "FinSMEs, funding announcements (https://www.finsmes.com/): search site:finsmes.com \"<company name>\" funding, adding city, sector, founder or lead investor if ambiguous; "
    "capture amount, currency, stage, investors and date, and cross-check with a company or investor announcement.",
    "Company, investor and customer websites, for traction: News, Press, Customers, Case Studies pages, or site:<company-domain> (\"revenue\" OR \"ARR\" OR \"customers\"), and site:<customer-domain> \"<startup name>\" for known customers. "
    "Keep documented adoption separate from disclosed paying customers, revenue, ARR or churn.",
]


def _numbered(items: list[str]) -> str:
    return " ".join(f"{i}) {s}" for i, s in enumerate(items, 1))


class CommercialAnalyst_Agent(SpecAgent):
    name = AgentName.COMMERCIAL_ANALYST
    tools = ("tavily_search", "tavily_funding_search", "tavily_page_extractor",)

    tasks_def = {
        "main": TaskDef(
            description=(
                "Review the commercial aspects of the target company: {topic}. "
                f"{CONTEXT_FIRST} "
                "Cover market, competitors, pricing, revenue model, go-to-market, traction, financial figures and funding; product/technology and team belong to other specialists. "
                "For financial and funding data, first identify the registered legal name, country and registration number, and search the official registers by number. "
                "If you search by brand name, confirm the match against the company's website, location or registered office, otherwise mark the figures as to be confirmed. "
                "Use these free sources, with the search and page extractor tools (Crunchbase, Dealroom and Openapi need a licence: do not guess their data): "
                f"{_numbered(FINANCIAL_SOURCES)} "
                "For each finding record metric, value, currency or unit, period or event date, the direct document or article URL, and whether it is filed, announced or estimated."
            ),
            expected_output=(
                "A markdown report with: a short summary; "
                "a 'Legal entity' line (legal name, country, registration number, how the match was confirmed, confidence); "
                "the findings as a list, each with its source URL, access date, metric, value, currency or unit, period or event date, "
                "status (verified, company claim or to be confirmed) and, for figures, filed, announced or estimated; "
                "sections for Market and competitors, Financials and revenue, Funding rounds and investors, and Commercial traction; "
                "and a 'Missing information' list of the items to request in the data room."
            ),
        ),
    }
