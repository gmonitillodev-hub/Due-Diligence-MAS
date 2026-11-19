from typing import Optional
import time

from crewai import Agent, Crew, Process, Task
from crewai.llms.base_llm import BaseLLM

from due_diligence_mas.mas_definition.agents.spec import SpecAgent
from due_diligence_mas.mas_definition.crewai_fr.utils import is_verbose
from due_diligence_mas.mas_definition.utils.llm_cost import summarize_cost
from due_diligence_mas.utils.logger import log_crew


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
        log_crew(self.name, "start", agents=len(self.crew_agents), tasks=len(self.crew_tasks))
        start = time.perf_counter()
        try:
            result = self.crew.kickoff()
        except Exception as e:
            log_crew(self.name, "failed", elapsed_s=round(time.perf_counter() - start, 2), error=e)
            raise
        self.metrics = self._collect_metrics(time.perf_counter() - start)
        log_crew(
            self.name, "end", elapsed_s=self.metrics["duration_s"], llm_calls=self.metrics["llm_calls"],
            tokens=self.metrics["tokens"]["total"], cost_usd=self.metrics["cost_usd"]["total"],
        )
        return result

    def _usage_by_model(self) -> dict:
        """Tokens by model, from the LLM of every agent: the same source of `crew.token_usage`, which is not split by model."""
        agents = [*self.crew.agents, *([self.crew.manager_agent] if self.crew.manager_agent else [])]
        models: dict[str, dict[str, int]] = {}
        for llm in {id(agent.llm): agent.llm for agent in agents}.values():
            if isinstance(llm, BaseLLM):
                usage = llm.get_token_usage_summary()
                totals = models.setdefault(llm.model, {"prompt_tokens": 0, "completion_tokens": 0})
                totals["prompt_tokens"] += usage.prompt_tokens
                totals["completion_tokens"] += usage.completion_tokens
        return models

    def _collect_metrics(self, duration_s: float) -> dict:
        usage = self.crew.token_usage
        models = self._usage_by_model()
        return {
            "name": self.name,
            "duration_s": round(duration_s, 2),
            "llm_calls": usage.successful_requests,
            "tokens": {
                "prompt": usage.prompt_tokens,
                "completion": usage.completion_tokens,
                "total": usage.total_tokens,
            },
            "models": models,
            "cost_usd": summarize_cost(models),
        }

    def print_crew_info(self):
        print("Crew Agents:")
        for agent in self.crew_agents:
            print(f"- {agent.role}")

        print("\nCrew Tasks:")
        for task in self.crew_tasks:
            print(f"- {task.description}")
