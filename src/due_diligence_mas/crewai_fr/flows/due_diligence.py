from crewai.flow.flow import Flow, start, listen, router, or_
from due_diligence_mas.classes import CompanyInfo, ProfiledCompany, CompanyProfile
from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.crews.analyst import AnalystCrew
from due_diligence_mas.crewai_fr.crews.debate import DebateCrew
from due_diligence_mas.crewai_fr.crews.profiler import ProfilerCrew
from due_diligence_mas.crewai_fr.crews.writer import MemoWriterCrew
from due_diligence_mas.crewai_fr.tools.file_generator import generate_memo_file
from due_diligence_mas.crewai_fr.utils import is_verbose
from due_diligence_mas.utils.request_handling import print_welcome_message, request_company_info
from pydantic import BaseModel

from typing import Optional

class DueDiligenceFlow_State(BaseModel):
    
    company_info: Optional[CompanyInfo] = None
    
    # Profiling output
    profile: Optional[CompanyProfile] = None
    
    # Results of the analysis and debate
    analysis_results: Optional[str] = None
    analysis_usage_info: Optional[str] = None
    analysis_total_time: Optional[str] = None
    
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
    
        return self.state.company_info
    
    @listen(initialize_flow)
    def profile_company(self):
        """ 
            Profile the target company.
        """
        
        print(f"\n  Profiling the target company: {self.state.company_info.company_name}...\n")
                
        analyst_crew = ProfilerCrew(company_info=self.state.company_info)
                    
        report = analyst_crew.run_crew()
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

        self.state.analysis_results = report
        self.state.analysis_usage_info = str(analyst_crew.crew.token_usage)

        return self.state.analysis_results
    
    @router(analyze_company)
    def human_approval(self):
        
        print(f"{'='*80}")
        print("\n   Here you can evaluate the analysis before proceeding with automatic debate. ")
        print("\n   Analysis produced: \n")
        print(f"         {self.state.analysis_results}")
        
        is_approved = True if input(f"\n    Can I proceed with the debate phase (y/n) ? ") == "y" else False
        
        return "debate" if is_approved else "final_report"
    
    @listen("debate")
    def run_debate(self):
        print(f"\n{'-'*80}")
        print(f"    Running debate crew...")
        
        debate_crew = DebateCrew(
                args={
                    "analysis": self.state.analysis_results
                }
            )
            
        print("\n   Running the crew...")
        result = debate_crew.run_crew()                
        self.state.debate_results = result.raw
        
        return result
    
    @listen(or_("final_report", run_debate))
    def generate_final_report(self):
        print(f"\n Due diligence stopped ...")
        
        if not self.state.analysis_results:
            raise ValueError("Analysis not produced")
        
        memo_crew = MemoWriterCrew(
            args={
                    "analysis": self.state.analysis_results,
                    "debate": self.state.debate_results if self.state.debate_results else "Debate not performed"
            }
        )
          
        result = memo_crew.run_crew()
        self.state.final_report = result.raw
        self.state.final_report_path = str(
            generate_memo_file(self.state.company_info.company_name, self.state.final_report)
        )
        print(f"\n Memo saved to: {self.state.final_report_path}")
    
        return self.state.final_report
    
def main():
    flow = DueDiligenceFlow(tracing=True, suppress_flow_events=not is_verbose("flow"))
    flow.kickoff()


if __name__ == "__main__":
    main()

