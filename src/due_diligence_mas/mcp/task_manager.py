import asyncio
import os
from uuid import UUID

from mcp.server.fastmcp import FastMCP

from due_diligence_mas.mcp.models import Priority, Task
from due_diligence_mas.mcp.repository import TASKS_DIR, save_task
from due_diligence_mas.mcp.users import User, get_mock_users
from due_diligence_mas.utils.logger import log_mcp_task, setup_logger

TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")  # stdio | streamable-http
HOST = os.getenv("MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_PORT", "8200"))

mcp = FastMCP("Task manager", host=HOST, port=PORT)


@mcp.tool()
def get_users() -> list[User]:
    """
        Get available users of task manager system

        Returns:
            List of users
    """
    users = get_mock_users()
    log_mcp_task("get_users", "done", count=len(users))
    return users


@mcp.tool()
def create_task(assignee: str, description: str, priority: str) -> Task:
    """
        Create a task and save it as a JSON file named after the task id

        Args:
            assignee: UUID of the user the task is assigned to
            description: Task description
            priority: HIGH, MEDIUM or LOW

        Returns:
            The created task
    """
    log_mcp_task("create_task", "start", assignee=assignee, priority=priority)
    task = Task(
        assignee=UUID(assignee),
        description=description,
        priority=Priority(priority.upper()),
    )
    path = save_task(task)
    log_mcp_task("create_task", "saved", task_id=task.id, path=path)
    return task


def main():
    setup_logger("mcp_task", enable_console=True)  # console goes to stderr, stdout stays free for stdio
    tools = [t.name for t in asyncio.run(mcp.list_tools())]
    if TRANSPORT == "stdio":
        log_mcp_task("server", "starting", transport=TRANSPORT, port="n/a (stdio)", tools=tools, tasks_dir=TASKS_DIR)
    else:
        log_mcp_task("server", "starting", transport=TRANSPORT, url=f"http://{HOST}:{PORT}{mcp.settings.streamable_http_path}", tools=tools, tasks_dir=TASKS_DIR)
    mcp.run(transport=TRANSPORT)
