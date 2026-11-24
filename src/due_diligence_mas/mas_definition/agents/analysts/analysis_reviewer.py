from due_diligence_mas.mas_definition.agents.analysts.analyst_supervisor import AnalystSupervisor
from due_diligence_mas.mas_definition.agents.dd_agent import TaskDef
from due_diligence_mas.mas_definition.classes.company import AnalysisReview
from due_diligence_mas.mas_definition.constants.review import ANALYSIS_REVIEW_CRITERIA, TASK_CREATION_INSTRUCTIONS


class AnalysisReviewer_Agent(AnalystSupervisor):
    """The supervisor acting as a regular agent: scores the aggregated analysis and, if it decides so, creates follow-up tasks with the task manager tools."""

    delegation = False

    tasks_def = {
        "review": TaskDef(
            description=f"{ANALYSIS_REVIEW_CRITERIA}\n\nYou have task manager tools. {TASK_CREATION_INSTRUCTIONS}\n\n{{topic}}",
            expected_output="The analysis review: completeness score, missing items and a short summary.",
            output_schema=AnalysisReview,
            tools=("mcp_tasks",),
        ),
    }
