# Constraints appended to the backstory of the analysts that search the web
RESEARCH_RIGOR = [
    "Retrieve data thoroughly, but a missing item never blocks you: for each item try up to 3 different approaches (other queries, the official site and its sub-pages, other sources or tools), then move on.",
    "Never repeat a search that already failed and never invent data.",
    "An item still not found goes in 'Missing information' as 'Not found after search: <sources tried>' ('Access required' if the document is gated); the report is always completed.",
]

# Output shared by the analysts' reports
ANALYST_REPORT_FORMAT = (
    "A markdown report with: a short summary; the findings as a list, each with its source URL, access date and status "
    "(verified, company claim or to be confirmed); and a 'Missing information' list."
)

# Shared by the analysts' tasks: the context already holds part of the work
CONTEXT_FIRST = "Start from the provided context (URLs, findings, missing items) and search only what is absent or missing there."
