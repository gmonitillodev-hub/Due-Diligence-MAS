from due_diligence_mas.mas_definition.agents.spec import SpecAgent, TaskDef
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName


class CommercialAnalyst_Agent(SpecAgent):
    name = AgentName.COMMERCIAL_ANALYST
    tools = ("tavily_search", "tavily_funding_search", "tavily_page_extractor",)

    tasks_def = {
        "main": TaskDef(
            description=(
                "Review the commercial aspects of the target company: {topic}. "
                "Start from the provided context (official URLs, findings, missing items): search only for information that is absent or listed as missing, and do not repeat searches already covered by the context. "
                "Cover market, competitors, pricing, revenue model, go-to-market, traction, financial figures and funding. "
                "Stay within commercial topics: product/technology and team belong to other specialists. "
                "Financial and funding research uses the free web sources below, through the search and page extractor tools; no API key is available. "
                "Before collecting data, identify the registered legal name, country of incorporation and registration number if available. "
                "Search by registration number first on the official registers. If you search by brand name, confirm the match against the company's website, location or registered office; if the match stays uncertain, mark the figures as to be confirmed. "
                "1) Companies House, UK annual accounts (https://find-and-update.company-information.service.gov.uk/): search the company number or registered name, open the company, Filing history > Accounts, and the PDF of the relevant period (iXBRL when available). "
                "Look for turnover, profit or loss and balance-sheet figures; record the financial year-end and whether the accounts cover the company or the group. Small or micro-company filings may omit the income statement. "
                "2) DATA INPI, French annual accounts (https://data.inpi.fr/recherche_avancee/entreprises): enter the nine-digit Siren, or the name in 'Dénomination' and confirm the location; open the record, 'Documents associés', 'comptes annuels' or 'bilans'. "
                "Opening documents needs a free account: if the session is not authenticated, record the company record URL and flag the accounts for manual retrieval. "
                "3) Tech.eu Funding Explorer, European rounds (https://funding.tech.eu/companies): search the brand name, open the matching profile and confirm country and website; in 'Funding rounds' open each round and capture date, stage, amount, investors and cited source. "
                "Keep equity, debt and grants distinct; when the site shows a euro conversion, verify the original currency in the cited announcement. "
                "4) SEC EDGAR, U.S. private offerings (https://www.sec.gov/edgar/search/): search the issuer's legal name or CIK, filing types D and D/A (or the 'Form' filter); confirm the issuer, open section 13 'Offering and Sales Amounts' and record 'Total Amount Sold' and the filing date. "
                "Check the amendments of the same offering: use the latest amount and never count the original and the amended filing as separate rounds. "
                "5) FinSMEs, funding announcements (https://www.finsmes.com/): web search site:finsmes.com \"<company name>\" funding, adding city, sector, founder or lead investor if the name is ambiguous; "
                "capture amount, currency, stage, investors and publication date, and cross-check with a company or investor announcement when available. "
                "6) Company, investor and customer websites, for commercial traction: look under News, Press, Customers, Case Studies; without a site search try site:<company-domain> (\"revenue\" OR \"ARR\" OR \"customers\"), and for an identified customer site:<customer-domain> \"<startup name>\". "
                "Record documented adoption separately from explicitly disclosed paying customer counts, revenue, ARR or churn. "
                "Crunchbase, Dealroom and Openapi need a licence or a paid API and are not reachable: do not guess their data. "
                "For each finding record the metric, value, currency or unit, reporting period or event date, and the direct document or article URL, and label the evidence as filed, announced or estimated. "
                "If a figure is missing, record 'Not disclosed in the sources reviewed'. If a document could not be opened, record 'Access required'."
            ),
            expected_output=(
                "A markdown report with: a short summary; "
                "a 'Legal entity' line (legal name, country, registration number, how the match was confirmed, match confidence); "
                "the findings as a list, each with its source URL, access date, metric, value, currency or unit, reporting period or event date, "
                "whether it is verified, a company claim or to be confirmed, and, for figures, whether it is filed, announced or estimated; "
                "separate sections for Financials and revenue, Funding rounds and investors, and Commercial traction, besides market and competitors; "
                "and a 'Missing information' list, where every missing figure is marked 'Not disclosed in the sources reviewed' or 'Access required', "
                "each as an item to request in the data room."
            ),
        ),
    }
