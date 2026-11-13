from crewai.flow.flow import Flow, start, listen, router
from due_diligence_mas.constants.agents_definition import AgentName
from due_diligence_mas.crewai_fr.crews.analyst import AnalystCrew
from pydantic import BaseModel
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
        print("-" * 80)
        print(f"{'Due Diligence Flow':^80}")
        print("\n   Welcome to the Due Diligence Flow. \n This flow will guide you through the process of \nanalyzing a target company, reviewing its technology, commercial aspects,\n and team dynamics, and generating a comprehensive report.\n")
        print("-" * 80)
    
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
        analyst_crew.print_crew_info()
            
        print("\nRunning the crew...")
        result = analyst_crew.run_crew()
                    
        self.state.analysis_results = f"Analysis results for {self.state.company_name}. \n {result.raw}"
        self.state.analysis_usage_info = f"Tokens Used: {result.token_usage}"
        #self.state.analysis_total_time = f"Total Time: {result.total_time}"

if __name__ == "__main__":
    flow = DueDiligenceFlow(tracing=True)
    flow.kickoff()