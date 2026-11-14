from pathlib import Path
import re

def generate_memo_file(company_name: str, final_report: str) -> Path:
    """
        Store the memo as a markdown file in the current working directory.

        Args:
            company_name: Name of the analyzed company
            final_report: Memo produced by the Memo Writer

        Returns:
            Path of the stored file
    """
    safe_name = re.sub(r"[^\w\-]+", "_", company_name or "company").strip("_")
    report_path = Path.cwd() / f"due_diligence_{safe_name}.md"
    report_path.write_text(final_report, encoding="utf-8")

    return report_path
