from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from due_diligence_mas.mas_definition.agents import BaseAgent
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.crewai_fr.utils import agent_limits, backstory_builder, extract_agent


@dataclass(frozen=True)
class TaskDef:
    """Framework-agnostic task definition. `{topic}` in `description` is replaced at build time."""

    description: str
    expected_output: str
    output_schema: Optional[type[BaseModel]] = None
    bind_agent: bool = True


class SpecAgent(BaseAgent):
    """
    Agent defined only by data: subclasses set the class attributes, the framework adapters build the objects.

    Attributes:
        name: agent name, key of the agents catalogue.
        tools: tool keys, resolved by each adapter.
        delegation: whether the agent can delegate work.
        tasks_def: task definitions by key; `build_tasks` picks one by key.
    """

    name: AgentName
    tools: tuple[str, ...] = ()
    delegation: bool = False
    tasks_def: dict[str, TaskDef] = {}

    def __init__(self, framework: Framework = Framework.CREW_AI, task="main"):
        self.framework = framework
        self.spec = extract_agent(self.name.value)
        self.backstory = backstory_builder(self.name.value)
        self.limits = agent_limits(self.name.value)
        self.tasks = []
        self.agent = self._adapter().build_agent(self, task)

    def crewai_kwargs(self) -> dict:
        """Extra crewai.Agent arguments for agents that need them."""
        return {}

    def _adapter(self):
        # Imported lazily so only the selected framework needs to be installed
        match self.framework:
            case Framework.CREW_AI:
                from due_diligence_mas.mas_definition.agents.adapters import crewai as adapter
            case Framework.LANG_GRAPH:
                from due_diligence_mas.mas_definition.agents.adapters import langgraph as adapter
            case _:
                raise ValueError(f"Unsupported framework: {self.framework}")
        return adapter

    def get_agent(self):
        return self.agent

    def get_tasks(self):
        return self.tasks

    def build_tasks(self, topic: str = "", context: list = [], key: str = "main"):
        if key not in self.tasks_def:
            raise KeyError(f"Unknown task '{key}' for {self.name.value}. Available: {', '.join(self.tasks_def)}")
        self.tasks = self._adapter().build_tasks(self, self.tasks_def[key], topic, context)
