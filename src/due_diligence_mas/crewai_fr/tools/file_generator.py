from pathlib import Path
import re
from crewai.tools import tool

@tool('generate_memo_file')
def generate_memo_file(company_name: str, final_report: str):
    """ 
        Generate and store a markdown file based on the report produced
        
        Args:
            company_name: Name of the analyzed company
            final_report: Report produced after memo refactor
            
        Returns:
            Path of the stored file
    """
    safe_name = re.sub(r"[^\w\-]+", "_", company_name or "company").strip("_")
    report_path = Path.cwd() / f"due_diligence_{safe_name}.md"
    report_path.write_text(
        f"{final_report}",
        encoding="utf-8",
    )
    
    return report_path