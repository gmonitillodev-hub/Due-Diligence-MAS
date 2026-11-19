import os

from crewai.flow.flow import Flow, start, listen, router, or_
from due_diligence_mas.mas_definition.classes import CompanyInfo, ProfiledCompany, CompanyProfile
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.crewai_fr.crews.analyst import AnalystCrew
from due_diligence_mas.mas_definition.crewai_fr.crews.debate import DebateCrew
from due_diligence_mas.mas_definition.crewai_fr.crews.profiler import ProfilerCrew
from due_diligence_mas.mas_definition.crewai_fr.crews.writer import MemoWriterCrew
from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.utils.execution_store import save_execution
from due_diligence_mas.mas_definition.utils.llm_cost import summarize_cost
from due_diligence_mas.mas_definition.crewai_fr.utils import is_verbose
from due_diligence_mas.mas_definition.utils.request_handling import print_welcome_message, request_company_info
from due_diligence_mas.utils.logger import log_crew
from pydantic import BaseModel

from typing import Optional

class DueDiligenceFlow_State(BaseModel):
    
    company_info: Optional[CompanyInfo] = None
    
    # Profiling output
    profile: Optional[CompanyProfile] = None
    
    # Results of the analysis and debate
    analysis_results: Optional[str] = None
    # Metrics of every executed crew, in execution order
    crews_metrics: list[dict] = []
    
    debate_results: Optional[str] = None  
    final_report: Optional[str] = None
    final_report_path: Optional[str] = None

class DueDiligenceFlow(Flow[DueDiligenceFlow_State]):
    
    @start()
    def initialize_flow(self):
        """
        Initialize the due diligence flow.
        """
        print_welcome_message()
        
        self.state.company_info = request_company_info()
        log_crew("flow", "initialized", company=self.state.company_info.company_name)
    
        return self.state.company_info
    
    @listen(initialize_flow)
    def profile_company(self):
        """ 
            Profile the target company.
        """
        
        print(f"\n  Profiling the target company: {self.state.company_info.company_name}...\n")
        log_crew("flow", "profile_company")
                
        analyst_crew = ProfilerCrew(company_info=self.state.company_info)
                    
        report = analyst_crew.run_crew()
        self.state.crews_metrics.append(analyst_crew.metrics)
        profile = report.pydantic
        print(f"Report > {profile.model_dump_json(indent=2) if profile else report.raw}")
        self.state.profile = profile
        
        return profile
        
    @listen(profile_company)
    def analyze_company(self):
        """
        Analyze the target company.
        """
        print(f"\n  Analyzing the target company: {self.state.company_info.company_name}...\n")
        log_crew("flow", "analyze_company")
        
        analyst_crew = AnalystCrew(
            company=ProfiledCompany(
                company_info=self.state.company_info,
                company_profile=self.state.profile
            ),
            required_agents=[
                    AgentName.TECH_REVIEWER.value, 
                    AgentName.COMMERCIAL_ANALYST.value,
                    AgentName.TEAM_ANALYST.value
                ]
            )
            
        report = analyst_crew.run_crew()
        self.state.crews_metrics.append(analyst_crew.metrics)

        self.state.analysis_results = report

        return self.state.analysis_results
    
    @router(analyze_company)
    def human_approval(self):
        
        print(f"{'='*80}")
        print("\n   Here you can evaluate the analysis before proceeding with automatic debate. ")
        print("\n   Analysis produced: \n")
        print(f"         {self.state.analysis_results}")
        
        is_approved = True if input(f"\n    Can I proceed with the debate phase (y/n) ? ") == "y" else False
        
        log_crew("flow", "human_approval", decision="debate" if is_approved else "final_report")
        return "debate" if is_approved else "final_report"
    
    @listen("debate")
    def run_debate(self):
        print(f"\n{'-'*80}")
        print(f"    Running debate crew...")
        log_crew("flow", "run_debate")
        
        debate_crew = DebateCrew(
                args={
                    "analysis": self.state.analysis_results
                }
            )
            
        print("\n   Running the crew...")
        result = debate_crew.run_crew()
        self.state.crews_metrics.append(debate_crew.metrics)                
        self.state.debate_results = result.raw
        
        return result
    
    @listen(or_("final_report", run_debate))
    def generate_final_report(self):
        print(f"\n Due diligence stopped ...")
        log_crew("flow", "generate_final_report")
        
        if not self.state.analysis_results:
            raise ValueError("Analysis not produced")
        
        memo_crew = MemoWriterCrew(
            args={
                    "analysis": self.state.analysis_results,
                    "debate": self.state.debate_results if self.state.debate_results else "Debate not performed"
            }
        )
          
        result = memo_crew.run_crew()
        self.state.crews_metrics.append(memo_crew.metrics)
        self.state.final_report = result.raw
        self.state.final_report_path = str(
            save_execution(
                self.state.company_info.company_name,
                Framework.CREW_AI,
                self.state.final_report,
                self._execution_metrics(),
            )
        )
        print(f"\n Execution saved to: {self.state.final_report_path}")
        log_crew("flow", "completed", execution_folder=self.state.final_report_path)
    
        return self.state.final_report

    def _execution_metrics(self) -> dict:
        """Totals over the crews (human approval time is outside the crews, so it is not counted) and the split by crew."""
        crews = self.state.crews_metrics
        prompt = sum(c["tokens"]["prompt"] for c in crews)
        completion = sum(c["tokens"]["completion"] for c in crews)
        models: dict[str, dict[str, int]] = {}
        for crew in crews:
            for model, usage in crew["models"].items():
                totals = models.setdefault(model, {"prompt_tokens": 0, "completion_tokens": 0})
                totals["prompt_tokens"] += usage["prompt_tokens"]
                totals["completion_tokens"] += usage["completion_tokens"]
        return {
            "total_time_s": round(sum(c["duration_s"] for c in crews), 2),
            "llm_calls": sum(c["llm_calls"] for c in crews),
            "tokens": {"prompt": prompt, "completion": completion, "total": prompt + completion},
            "cost_usd": summarize_cost(models),
            "crews": crews,
            "tracing": {"crewai_tracing_enabled": os.getenv("CREWAI_TRACING_ENABLED", "").lower() == "true"},
        }
    
def main():
    flow = DueDiligenceFlow(tracing=True, suppress_flow_events=not is_verbose("flow"))
    flow.kickoff()


if __name__ == "__main__":
    main()

