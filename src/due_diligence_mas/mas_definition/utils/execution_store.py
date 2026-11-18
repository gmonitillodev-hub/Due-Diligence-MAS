import json
import os
import re
from datetime import datetime
from pathlib import Path

from due_diligence_mas.mas_definition.constants.common import Framework

# <repo>/doc/executions, overridable with EXECUTIONS_DIR
DEFAULT_EXECUTIONS_DIR = Path(__file__).resolve().parents[4] / "doc" / "executions"


def save_execution(company_name: str, framework: Framework, memo: str, metrics: dict) -> Path:
    """
    Store an execution in its own folder: `memo.md` (the final memo as is) and `metrics.json`.

    Args:
        company_name: Name of the analyzed company
        framework: Framework that ran the execution
        memo: Final memo in markdown
        metrics: Timing, LLM calls, tokens and tracing info of the execution

    Returns:
        Path of the execution folder
    """
    safe_name = re.sub(r"[^\w\-]+", "_", company_name or "company").strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path(os.getenv("EXECUTIONS_DIR") or DEFAULT_EXECUTIONS_DIR)
    folder = base / f"{safe_name}_{framework.value}_{timestamp}"
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "memo.md").write_text(memo, encoding="utf-8")
    payload = {"company": company_name, "framework": framework.value, **metrics}
    (folder / "metrics.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return folder
