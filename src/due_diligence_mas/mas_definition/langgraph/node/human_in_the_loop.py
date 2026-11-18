from typing import Optional

from due_diligence_mas.mas_definition.classes.company import AnalysisReview
from due_diligence_mas.mas_definition.constants.langgraph import MEMO_WRITER_NODE
from due_diligence_mas.mas_definition.langgraph.classes.shared_state import DueDiligence_State
from due_diligence_mas.mas_definition.langgraph.node.supervisor import debate_entry_node
from langgraph.types import interrupt
from rich.console import Console
from rich.markdown import Markdown


def _print_preview(analysis: str, review: Optional[AnalysisReview]):
    """Print the supervisor's analysis review (score, missing items) and the analysis as formatted markdown."""
    console = Console()
    if review:
        missing = "\n".join(f"- {m}" for m in review.missing) or "- none"
        console.print(Markdown(f"## Supervisor review: completeness score {review.score}/10\n\n{review.summary}\n\n**Missing:**\n{missing}\n\n---"))
    console.print(Markdown(analysis or "_No analysis available_"))


def human_review_node(state: DueDiligence_State):
    """Pause the graph and wait for the human decision on the analysis; resumes with the decision as value."""
    review = state.supervision.analysis_review
    _print_preview(state.analysis_results, review)

    human_decision = interrupt({
        "message": "The analysis is complete. Review the results and decide how to proceed.",
        "analysis_preview": state.analysis_results,
        "analysis_review": review.model_dump() if review else None,
        "options": {
            "Proceed": "Approve and proceed with the debate",
            "End": "Skip the debate and write the memo from the analysis only",
        },
    })
    return {"human_decision": str(human_decision).strip().lower()}


def preview_and_confirm_router(state: DueDiligence_State):
    """Proceed goes on to the debate, anything else goes straight to the memo writer."""
    if state.human_decision == "proceed":
        return debate_entry_node()
    return MEMO_WRITER_NODE
