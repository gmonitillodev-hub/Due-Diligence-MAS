from typing import Optional
import time

from crewai import Agent, Crew, Process, Task

from due_diligence_mas.mas_definition.agents.spec import SpecAgent
from due_diligence_mas.mas_definition.crewai_fr.utils import is_verbose


class BaseCrew:
    """
    Common skeleton of the crews: subclasses implement `_setup` and register their agents with `add`.
    Agents are added in execution order.
    """

    name: str = "Crew"
    process: Process = Process.sequential
    manager: Optional[SpecAgent] = None

    def __init__(self):
        self.crew_agents: list[Agent] = []
        self.crew_tasks: list[Task] = []
        self._setup()

    def _setup(self):
        raise NotImplementedError

    def add(self, agent: SpecAgent, topic, *, context: Optional[list[Task]] = None, key: str = "main") -> SpecAgent:
        """Register the agent and build its tasks; the task context is decided by the calling crew."""
        agent.build_tasks(topic, context=context, key=key)
        self.crew_agents.append(agent.get_agent())
        self.crew_tasks.extend(agent.get_tasks())
        return agent

    def _crew_kwargs(self) -> dict:
        kwargs = {}
        if self.manager is not None:
            kwargs["manager_agent"] = self.manager.get_agent()
        return kwargs

    def build_crew(self):
        self.crew = Crew(
            name=self.name,
            agents=self.crew_agents,
            tasks=self.crew_tasks,
            process=self.process,
            tracing=True,
            verbose=is_verbose("crew"),
            **self._crew_kwargs(),
        )

    def run_crew(self):
        if not hasattr(self, "crew"):
            self.build_crew()
        start = time.perf_counter()
        result = self.crew.kickoff()
        self.metrics = self._collect_metrics(time.perf_counter() - start)
        return result

    def _collect_metrics(self, duration_s: float) -> dict:
        usage = self.crew.token_usage
        return {
            "name": self.name,
            "duration_s": round(duration_s, 2),
            "llm_calls": usage.successful_requests,
            "tokens": {
                "prompt": usage.prompt_tokens,
                "completion": usage.completion_tokens,
                "total": usage.total_tokens,
            },
        }

    def print_crew_info(self):
        print("Crew Agents:")
        for agent in self.crew_agents:
            print(f"- {agent.role}")

        print("\nCrew Tasks:")
        for task in self.crew_tasks:
            print(f"- {task.description}")
