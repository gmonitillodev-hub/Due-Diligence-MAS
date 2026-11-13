from pathlib import Path
import re

def generate_memo_file(state):
    safe_name = re.sub(r"[^\w\-]+", "_", state.company_name or "company").strip("_")
    report_path = Path.cwd() / f"due_diligence_{safe_name}.md"
    report_path.write_text(
        f"# Due Diligence Report: {state.company_name}\n\n"
        f"- **Website:** {state.company_site or 'N/A'}\n"
        f"- **Sector:** {state.company_sector or 'N/A'}\n"
        f"## Analysis\n\n{state.final_report}\n"
        f"{f'## Debate \n\n{state.debate_results}' if state.debate_results else '## !! Debate not produced'}\n",
        encoding="utf-8",
    )
    
    return report_path