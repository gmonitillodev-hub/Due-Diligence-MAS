import sys

TASK_SERVER_COMMAND = sys.executable
TASK_SERVER_ARGS = ["-c", "from due_diligence_mas.mcp.task_manager import main; main()"]


async def get_task_tools():
    """LangChain tools (get_users, create_task) exposed by the task manager MCP server. MCP tools are async only."""
    from langchain_mcp_adapters.client import MultiServerMCPClient

    client = MultiServerMCPClient({"task_manager": {"transport": "stdio", "command": TASK_SERVER_COMMAND, "args": TASK_SERVER_ARGS}})
    return await client.get_tools()


def get_task_server_crewai():
    """CrewAI stdio config of the task manager MCP server."""
    from crewai.mcp import MCPServerStdio

    return MCPServerStdio(command=TASK_SERVER_COMMAND, args=TASK_SERVER_ARGS)
