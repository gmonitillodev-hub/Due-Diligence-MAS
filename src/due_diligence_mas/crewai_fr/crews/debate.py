from crewai import Agent, Task, Crew, Process, LLM
from due_diligence_mas.crewai_fr.agents.debate.debate_formatter import DebateFormatter_Agent
from due_diligence_mas.crewai_fr.agents.debate.debate_judge import DebateJudge_Agent
from due_diligence_mas.crewai_fr.agents.debate.opportunity_analyst import OpportunityAnalyst_Agent
from due_diligence_mas.crewai_fr.agents.debate.risk_analyst import RiskAnalyst_Agent
from due_diligence_mas.crewai_fr.utils import get_context_tasks

class DebateCrew():  
    """
        Crew for managing debate agents.
    """
    
    def __init__(self, args = {}, need_formatter: bool = True):
        
        self.topic = args
    
        self.crew_agents: list[Agent] = []
        self.crew_tasks: list[Task] = []
            
        self._initialize_agents(need_formatter)    
        self._build_tasks()

    def _initialize_agents(self, need_formatter: bool):
        """ 
            Initialize crew agents
        """
        
        if need_formatter:
            self.formatter_agent = DebateFormatter_Agent()
            self.crew_agents.append(self.formatter_agent.get_agent())
        
        self.opportunity_analyst = OpportunityAnalyst_Agent()
        self.crew_agents.append(self.opportunity_analyst.get_agent())    
        
        self.risk_analyst = RiskAnalyst_Agent()
        self.crew_agents.append(self.risk_analyst.get_agent())   
                
        self.debate_judge = DebateJudge_Agent()
        self.crew_agents.append(self.debate_judge.get_agent())   
        
    def _build_tasks(self):
        """ 
            Build tasks for each agent based on the topic and context
        """
            
        if hasattr(self, 'formatter_agent'):        
            self.formatter_agent.build_tasks(self.topic)
            self.crew_tasks.extend(self.formatter_agent.get_tasks())
         
        if hasattr(self, 'opportunity_analyst'):       
            self.opportunity_analyst.build_tasks(
                    self.topic, 
                    context=get_context_tasks(self.formatter_agent)
                )
            self.crew_tasks.extend(self.opportunity_analyst.get_tasks())
        
        if hasattr(self, 'risk_analyst'):       
            self.risk_analyst.build_tasks(
                    self.topic, 
                    context=get_context_tasks(
                        self.formatter_agent, 
                        self.opportunity_analyst
                        )
                )
            self.crew_tasks.extend(self.risk_analyst.get_tasks())
            
        if hasattr(self, 'debate_judge'):       
            self.debate_judge.build_tasks(
                self.topic, 
                context=get_context_tasks(
                    self.opportunity_analyst,
                    self.risk_analyst
                )
            )
            self.crew_tasks.extend(self.debate_judge.get_tasks())
            
    def build_crew(self):
        """
            Build the crew with the initialized agents and tasks
        """
        self.crew = Crew(
            name="Debate Crew",
            agents=self.crew_agents,
            tasks=self.crew_tasks,
            process=Process.sequential,
            tracing=True,
            verbose=True
        )
    
    def run_crew(self):
        """
            Run the crew to execute the tasks
        """
        if not hasattr(self, 'crew'):
            self.build_crew()
        
        return self.crew.kickoff()       
    
    def print_crew_info(self):
        print("Crew Agents:")
        for agent in self.crew_agents:
            print(f"- {agent.role}")
        
        print("\nCrew Tasks:")
        for task in self.crew_tasks:
            print(f"- {task.description}")
            
if __name__ == "__main__":
    crew = DebateCrew(
        args={
            "analysis":""" 
        
   ## 1. Company Overview                                                                                   │
│                                                                                                           │
│  | Item | Detail |                                                                                        │
│  |------|--------|                                                                                        │
│  | **Legal name** | Reply S.p.A. |                                                                        │
│  | **Headquarters** | Via G. B. Morgagni, 1 – 20141 Milano, Italy |                                       │
│  | **Founded** | 1996 (as “Reply”) |                                                                      │
│  | **Public listing** | Borsa Italiana – **MTA: REY** (since 2000) |                                      │
│  | **Sector** | Information‑technology services, consulting, system integration, digital transformation   │
│  |                                                                                                        │
│  | **Core business** | Design, implementation and management of end‑to‑end digital solutions (cloud,      │
│  data & AI, cybersecurity, IoT, blockchain, UX/UI, software engineering) for large enterprises and        │
│  public‑sector organisations. |                                                                           │
│  | **Geographic footprint** | 30+ countries – strong presence in Italy, Germany, France, United Kingdom,  │
│  Spain, Switzerland, United Arab Emirates, United States (via subsidiaries), and emerging offices in      │
│  Singapore, Brazil and Canada. |                                                                          │
│  | **Industry focus** | Banking & Financial Services, Insurance, Telecommunications, Media &              │
│  Entertainment, Energy & Utilities, Manufacturing & Automotive, Public Administration, Healthcare & Life  │
│  Sciences, Retail & Consumer Goods. |                                                                     │
│  | **Corporate structure** | Holding (Reply S.p.A.) + > 30 specialised subsidiaries (e.g., Reply, Reply   │
│  Digital Services, Reply Business Consulting, Reply Enterprise Solutions, Reply AI Lab, Reply Cloud,      │
│  Reply Security, Reply IoT, Reply Media, Reply Telecom, Reply Banking, Reply Insurance, Reply Energy).    │
│  Each subsidiary focuses on a specific technology domain or vertical market. |                            │
│                                                                                                           │
│  ---                                                                                                      │
│                                                                                                           │
│  ## 2. Product / Service Offering                                                                         │
│                                                                                                           │
│  | Category | Main Offerings (as described on the corporate website) |                                    │
│  |----------|--------------------------------------------------------|                                    │
│  | **Consulting & Strategy** | Digital transformation road‑maps, business‑process redesign, innovation    │
│  labs, change‑management programmes. |                                                                    │
│  | **Cloud & Infrastructure** | Cloud migration & modernisation (public, private, hybrid), Cloud‑native   │
│  application development, DevOps & CI/CD pipelines, Cloud‑cost optimisation, partnership services with    │
│  **Microsoft Azure**, **Amazon Web Services (AWS)**, **Google Cloud Platform (GCP)**. |                   │
│  | **Data & AI** | Data engineering, Big‑Data platforms, Advanced analytics, Machine‑learning model       │
│  development, AI‑as‑a‑service, Generative‑AI solutions (e.g., “Reply AI Studio”). |                       │
│  | **Cybersecurity** | Security assessment, Identity & Access Management, Threat‑intelligence,            │
│  SOC‑as‑a‑service, Zero‑Trust architecture, compliance (GDPR, ISO 27001). |                               │
│  | **Software Engineering** | Custom application development, API‑first architecture, Micro‑services,     │
│  Low‑code/no‑code platforms, Agile delivery, Quality‑assurance & testing. |                               │
│  | **IoT & Edge** | Connected‑device platforms, Industrial IoT, Smart‑city solutions, Edge‑computing, 5G  │
│  enablement. |                                                                                            │
│  | **Blockchain & Distributed Ledger** | Smart‑contract development, Tokenisation platforms,              │
│  Supply‑chain traceability solutions. |                                                                   │
│  | **UX/UI & Design** | Service‑design, Customer‑experience (CX) research, Interaction design,            │
│  Prototyping. |                                                                                           │
│  | **Industry‑specific Solutions** | • **Banking & Insurance** – Core‑system modernisation,               │
│  fraud‑detection AI, digital onboarding.<br>• **Telecom** – 5G network‑automation, OSS/BSS                │
│  transformation.<br>• **Energy** – Smart‑grid analytics, predictive maintenance.<br>• **Public Sector**   │
│  – E‑government platforms, citizen‑services portals. |                                                    │
│                                                                                                           │
│  ---                                                                                                      │
│                                                                                                           │
│  ## 3. Value Proposition                                                                                  │
│                                                                                                           │
│  1. **End‑to‑end digital expertise** – From strategy to implementation and managed services, delivered    │
│  by specialised subsidiaries that combine deep industry knowledge with cutting‑edge technology.           │
│  2. **European scale with local presence** – Over 10 000 professionals, most of them located in the       │
│  client’s country, enabling close collaboration and compliance with local regulations.                    │
│  3. **Strong ecosystem partnerships** – Gold/Platinum partners of Microsoft, AWS, Google Cloud, IBM,      │
│  SAP, Oracle, and leading system‑integrators, giving clients access to the latest platforms and           │
│  joint‑innovation programmes.                                                                             │
│  4. **Innovation‑first culture** – Dedicated “Reply Labs” (AI Lab, Cloud Lab, IoT Lab) that prototype     │
│  emerging technologies and co‑create proofs‑of‑concept with customers.                                    │
│  5. **Financial stability** – Listed on the Milan Stock Exchange, audited financial statements,           │
│  consistent revenue growth (> 10 % YoY on average 2019‑2023).                                             │
│                                                                                                           │
│  ---                                                                                                      │
│                                                                                                           │
│  ## 4. Target Customers                                                                                   │
│                                                                                                           │
│  | Segment | Typical Profile |                                                                            │
│  |---------|-----------------|                                                                            │
│  | **Large Enterprises** (≥ €1 bn revenue) | Multinational corporations in banking, telecom, energy,      │
│  manufacturing, and retail seeking large‑scale digital transformation, cloud migration, or AI‑driven      │
│  business models. |                                                                                       │
│  | **Mid‑size Corporations** (€200 m‑€1 bn) | Companies that have already adopted basic cloud services    │
│  and now need advanced analytics, cybersecurity, or industry‑specific platforms. |                        │
│  | **Public‑sector organisations** | Ministries, municipalities, health‑care agencies, and utilities      │
│  that require secure, compliant e‑government solutions and citizen‑centric services. |                    │
│  | **Technology Partners** | OEMs and platform providers (Microsoft, AWS, Google, SAP) that need          │
│  system‑integration and consulting capabilities to deliver joint solutions to end‑customers. |            │
│                                                                                                           │
│  ---                                                                                                      │
│                                                                                                           │
│  ## 5. Representative Use Cases (publicly disclosed)                                                      │
│                                                                                                           │
│  | Use‑Case | Customer (publicly named) | Solution Highlights |                                           │
│  |----------|---------------------------|---------------------|                                           │
│  | **AI‑driven fraud detection** | **UniCredit** (Banking) | Real‑time transaction monitoring, ML models  │
│  for anomaly detection, integration with core banking platform, 30 % reduction in false positives. |      │
│  | **5G network automation** | **Deutsche Telekom** (Telecom) | OSS/BSS transformation, automated         │
│  service‑provisioning, edge‑computing integration, 20 % faster rollout of new services. |                 │
│  | **Smart‑grid predictive maintenance** | **Enel** (Energy) | IoT sensors + Azure IoT Hub, predictive    │
│  analytics for turbine health, 15 % reduction in unplanned outages. |                                     │
│  | **Digital citizen portal** | **Comune di Milano** (Public sector) | End‑to‑end portal for permits,     │
│  payments, and service requests; built on a micro‑services architecture, 40 % increase in online          │
│  transactions. |                                                                                          │
│  | **Cloud‑native ERP migration** | **Barilla** (Food & Beverage) | Migration of SAP ECC to SAP S/4HANA   │
│  on Azure, DevOps pipeline, zero‑downtime cut‑over, 25 % cost saving on infrastructure. |                 │
│  | **Zero‑Trust security framework** | **Generali** (Insurance) | Identity‑centric security,              │
│  conditional‑access policies, SOC‑as‑a‑service, compliance with GDPR and ISO 27001. |                     │
│                                                                                                           │
│  *All use‑cases are taken from the “Case Studies” section of Reply’s corporate website (accessed 12 Nov   │
│  2026).*                                                                                                  │
│                                                                                                           │
│  ---          """
        }  
    )
    crew.print_crew_info()
    
    print("\nRunning the crew...")
    result = crew.run_crew()
    
    print("\nCrew Execution Result:")
    print(f"Tokens Used: {result.token_usage}")
    print(result)