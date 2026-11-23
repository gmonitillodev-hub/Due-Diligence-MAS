import os

from crewai.flow import Flow, start, listen, router, or_, HumanFeedbackPending, HumanFeedbackProvider, human_feedback
from due_diligence_mas.mas_definition.classes import CompanyInfo, ProfiledCompany, CompanyProfile
from due_diligence_mas.mas_definition.classes.company import AnalysisReview
from due_diligence_mas.mas_definition.constants.agents_definition import AgentName
from due_diligence_mas.mas_definition.crewai_fr.crews.analyst import AnalystCrew
from due_diligence_mas.mas_definition.crewai_fr.crews.debate import DebateCrew
from due_diligence_mas.mas_definition.crewai_fr.crews.profiler import ProfilerCrew
from due_diligence_mas.mas_definition.crewai_fr.crews.review import AnalysisReviewCrew
from due_diligence_mas.mas_definition.crewai_fr.crews.writer import MemoWriterCrew
from due_diligence_mas.mas_definition.constants.common import Framework
from due_diligence_mas.mas_definition.utils.execution_db import ExecutionStatus, create_execution, update_execution
from due_diligence_mas.mas_definition.utils.llm_cost import summarize_cost
from due_diligence_mas.mas_definition.crewai_fr.utils import is_verbose
from due_diligence_mas.mas_definition.utils.request_handling import request_company_info
from due_diligence_mas.utils.logger import log_crew
from pydantic import BaseModel, Field
from crewai.flow.persistence import SQLiteFlowPersistence


from functools import wraps
from typing import Optional

FLOW_DB_PATH = os.getenv("CREWAI_FLOW_DB_PATH", "due_diligence_crewai.db")
APPROVAL_ANSWERS = {"y", "yes", "proceed", "approve", "approved"}

def track_crew(run_crew):
    """Store the crew in progress on the execution row, then the metrics when it ends."""
    @wraps(run_crew)
    def wrapper(self, crew):
        update_execution(self.state.id, current_crew=crew.name)
        result = run_crew(self, crew)
        update_execution(self.state.id, metrics=self._execution_metrics())
        return result
    return wrapper

class DueDiligenceFlow_State(BaseModel):
    
    company_info: Optional[CompanyInfo] = None
    
    profile: Optional[CompanyProfile] = None
    
    analysis_results: Optional[str] = None
    analysis_review: Optional[AnalysisReview] = None
    crews_metrics: list[dict] = Field(default_factory=list)
    
    debate_results: Optional[str] = None  
    final_report: Optional[str] = None
    
class RestFeedbackProvider(HumanFeedbackProvider):
    def request_feedback(self, context, flow) -> str:
        raise HumanFeedbackPending(context=context)

class DueDiligenceFlow(Flow[DueDiligenceFlow_State]):
    
    @start()
    def initialize_flow(self):
        """
        Initialize the due diligence flow.
        """
        if self.state.company_info is None:
            self.state.company_info = request_company_info()
            
        log_crew("flow", "initialized", company=self.state.company_info.company_name)
        
        return self.state.company_info
    
    @listen(initialize_flow)
    def profile_company(self):
        """ 
            Profile the target company.
        """
        
        log_crew("flow", "profile_company")
                
        analyst_crew = ProfilerCrew(company_info=self.state.company_info)
                    
        report = self._run_crew(analyst_crew)
        profile = report.pydantic
        log_crew("flow", "profile_completed", profiled=profile is not None)
        self.state.profile = profile
        
        return profile
        
    @listen(profile_company)
    def analyze_company(self):
        """
        Analyze the target company.
        """
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
            
        report = self._run_crew(analyst_crew)
        self.state.analysis_results = report

        return self.state.analysis_results
    
    @listen(analyze_company)
    def review_analysis(self):
        """
        Completeness gate: score of the analysis, with follow-up tasks created by the reviewer if needed.
        """
        log_crew("flow", "review_analysis")

        review_crew = AnalysisReviewCrew(
            company=ProfiledCompany(company_info=self.state.company_info, company_profile=self.state.profile),
            analysis=self.state.analysis_results,
        )
        self.state.analysis_review = self._run_crew(review_crew)
        log_crew("flow", "analysis_reviewed", score=self.state.analysis_review.score, missing=len(self.state.analysis_review.missing))

        return self.state.analysis_results

    @listen(review_analysis)
    @human_feedback(     
          message="Please review the analysis and proceed or end the execution",
          provider=RestFeedbackProvider() 
    )
    def ask_human_review(self, analysis_results):
        return analysis_results
    
    @router(ask_human_review)
    def human_decision_router(self):
        feedback = self.last_human_feedback.feedback if self.last_human_feedback else ""
        is_approved = feedback.strip().lower() in APPROVAL_ANSWERS

        log_crew("flow", "human_approval", decision="debate" if is_approved else "final_report")
        return "debate" if is_approved else "final_report"
    
    @listen("debate")
    def run_debate(self):
        log_crew("flow", "run_debate")
        
        debate_crew = DebateCrew(
                args={
                    "analysis": self.state.analysis_results
                }
            )
            
        result = self._run_crew(debate_crew)
        self.state.debate_results = result.raw
        
        return result
    
    @listen(or_("final_report", run_debate))
    def generate_final_report(self):
        log_crew("flow", "generate_final_report")
        
        if not self.state.analysis_results:
            raise ValueError("Analysis not produced")
        
        memo_crew = MemoWriterCrew(
            args={
                    "analysis": self.state.analysis_results,
                    "debate": self.state.debate_results if self.state.debate_results else "Debate not performed"
            }
        )
          
        result = self._run_crew(memo_crew)
        self.state.final_report = result.raw
        update_execution(
            self.state.id,
            status=ExecutionStatus.COMPLETED,
            current_node=None,
            current_crew=None,
            metrics=self._execution_metrics(),
            memo_markdown=self.state.final_report,
        )
        log_crew("flow", "completed")
    
        return self.state.final_report

    @track_crew
    def _run_crew(self, crew):
        result = crew.run_crew()
        self.state.crews_metrics.append(crew.metrics)
        return result

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
    
def _close_execution(flow: DueDiligenceFlow, thread_id: str, result):
    """A paused flow returns HumanFeedbackPending: mark the execution as awaiting review."""
    if isinstance(result, HumanFeedbackPending):
        update_execution(
            thread_id,
            status=ExecutionStatus.AWAITING_REVIEW,
            current_node="ask_human_review",
            current_crew=None,
            metrics=flow._execution_metrics(),
            pending_review={
                "analysis": flow.state.analysis_results,
                "analysis_review": flow.state.analysis_review.model_dump() if flow.state.analysis_review else None,
                "options": ["proceed", "end"],
            },
        )
    return result

def run_due_diligence_flow(company_info: CompanyInfo, thread_id: str):
    """ 
        One instance per request is needed cause CrewAI is statefull
    """
    create_execution(thread_id, Framework.CREW_AI.value, company_info.company_name)
    flow = DueDiligenceFlow(
        tracing=os.getenv("CREWAI_TRACING_ENABLED", "").lower() == "true",
        suppress_flow_events=not is_verbose("flow"),
        persistence=SQLiteFlowPersistence(FLOW_DB_PATH),
    )
    try:
        result = flow.kickoff(inputs={"id": thread_id, "company_info": company_info})
    except Exception:
        update_execution(thread_id, status=ExecutionStatus.FAILED, metrics=flow._execution_metrics())
        raise
    return _close_execution(flow, thread_id, result)
    
def resume_due_diligence_flow(decision: str, thread_id: str):
    update_execution(thread_id, status=ExecutionStatus.RUNNING, pending_review=None)
    flow = DueDiligenceFlow.from_pending(thread_id, persistence=SQLiteFlowPersistence(FLOW_DB_PATH))
    try:
        result = flow.resume(decision)
    except Exception:
        update_execution(thread_id, status=ExecutionStatus.FAILED, metrics=flow._execution_metrics())
        raise
    return _close_execution(flow, thread_id, result)

if __name__ == "__main__":
    run_due_diligence_flow(request_company_info(), "local")

