import os
from crewai import LLM
from dotenv import load_dotenv

class LLM_PROVIDER():
    
    def __init__(self, provider="groq", reasoning="medium", temperature=0.2):
        
        load_dotenv()

        self.temperature = temperature
        
        match provider:
            case "groq":
                
                if os.getenv("GROQ_API_KEY") is None:
                    raise ValueError("GROQ_API_KEY environment variable is not set.")
                
                if reasoning == "medium":
                    self.model = "groq/llama-3.3-70b-versatile"
                elif reasoning == "high":
                    self.model = "groq/llama-3.3-70b-high-reasoning"
                else:
                    raise ValueError("Invalid reasoning level. Choose 'medium' or 'high'.")
              
            case "openai":
                if os.getenv("OPENAI_API_KEY") is None:
                    raise ValueError("OPENAI_API_KEY environment variable is not set.")
                
                if reasoning == "medium":
                    self.model = "gpt-4o"
                elif reasoning == "high":
                    self.model = "gpt-4o-reasoning"
                else:
                    raise ValueError("Invalid reasoning level. Choose 'medium' or 'high'.")
               
        self.llm = LLM(
                    model=self.model,
                    temperature=self.temperature,
                )

    def get_llm(self):
        return self.llm 
         