from crewai.flow.flow import Flow, start, listen, router, or_
from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.crews.analyst import AnalystCrew
from due_diligence_mas.crewai_fr.crews.debate import DebateCrew
from due_diligence_mas.crewai_fr.crews.writer import MemoWriterCrew
from due_diligence_mas.utils.create_memo_file import generate_memo_file
from pydantic import BaseModel
from dotenv import load_dotenv

from typing import Optional

class DueDiligenceFlow_State(BaseModel):
    
    # Company information to search and analyze
    company_name: Optional[str] = None
    company_site: Optional[str] = None
    company_sector: Optional[str] = None
    
    # Results of the analysis and debate
    analysis_results: Optional[str] = None
    analysis_usage_info: Optional[str] = None
    analysis_total_time: Optional[str] = None
    
    debate_results: Optional[str] = None  
    final_report: Optional[str] = None

class DueDiligenceFlow(Flow[DueDiligenceFlow_State]):
    
    def _print_welcome_message(self):
        print("=" * 80)
        print(f"{'Due Diligence Flow':^80}")
        print("\n   Welcome to the Due Diligence Flow. \n   This flow will guide you through the process of analyzing a target company,\n   reviewing its technology, commercial aspects, and team dynamics, and\n   generating a comprehensive report.\n")
        print("=" * 80)
        print("\n")
    
    @start()
    def initialize_flow(self):
        """
        Initialize the due diligence flow.
        """
        self._print_welcome_message()
        
        self.state.company_name = input("Enter the target company name: ")
        self.state.company_site = input("Enter the target company website (optional): ")
        self.state.company_sector = input("Enter the target company sector (optional): ")
        
        return True 
        
    @listen(initialize_flow)
    def analyze_company(self):
        """
        Analyze the target company.
        """
        print(f"\n  Analyzing the target company: {self.state.company_name}...\n")
        
        analyst_crew = AnalystCrew(
            args={
                "company_name": self.state.company_name,
                "company_site": self.state.company_site,
                "company_sector": self.state.company_sector
            },
            required_agents=[
                    AgentName.TECH_REVIEWER.value, 
                    AgentName.COMMERCIAL_ANALYST.value
                ]
            )
            
        result = analyst_crew.run_crew()
                    
        # result.raw only holds the last task output: merge all of them
        self.state.analysis_results = "\n\n".join(
            f"## {t.agent}\n\n{t.raw}" for t in result.tasks_output if t.raw
        ) or result.raw
        self.state.analysis_usage_info = result.token_usage
        
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
          
        self.state.final_report = memo_crew.run_crew()
    
        return self.state.final_report
    
if __name__ == "__main__":
    flow = DueDiligenceFlow(tracing=True)
    flow.kickoff()

