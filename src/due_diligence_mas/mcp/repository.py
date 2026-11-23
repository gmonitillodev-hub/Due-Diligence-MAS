from pathlib import Path

from due_diligence_mas.mcp.models import Task

TASKS_DIR = Path(__file__).resolve().parent / "tasks"


def save_task(task: Task) -> Path:
    """Store the task as <task_id>.json in the tasks folder."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    path = TASKS_DIR / f"{task.id}.json"
    path.write_text(task.model_dump_json(indent=2))
    return path
