import os
from crewai import LLM
from dotenv import load_dotenv

class GroqSafeLLM(LLM):
    """Strips crewai's `cache_breakpoint` flag, which Groq rejects via LiteLLM."""

    def _format_messages_for_provider(self, messages):
        cleaned = [
            {k: v for k, v in m.items() if k != "cache_breakpoint"}
            if isinstance(m, dict) else m
            for m in messages or []
        ]
        return super()._format_messages_for_provider(cleaned)


class LLM_PROVIDER():
    
    def __init__(self, provider="", reasoning="", temperature=0.2):
        
        load_dotenv()
        
        if reasoning == "": 
            reasoning = os.getenv("DEFAULT_REASONING_LEVEL", "medium")
            
        if provider == "":
            provider = os.getenv("DEFAULT_LLM_PROVIDER", "groq")

        self.temperature = temperature
        
        match provider:
            case "groq":
                
                if os.getenv("GROQ_API_KEY") is None:
                    raise ValueError("GROQ_API_KEY environment variable is not set.")
                
                if reasoning == "medium":
                    self.model = "groq/openai/gpt-oss-20b"
                elif reasoning == "high":
                    self.model = "groq/openai/gpt-oss-120b"
                else:
                    raise ValueError("Invalid reasoning level. Choose 'medium' or 'high'.")
                
                self.llm = GroqSafeLLM(
                                    model=self.model,
                                    temperature=self.temperature,
                                )
              
            case "openai":
                if os.getenv("OPENAI_API_KEY") is None:
                    raise ValueError("OPENAI_API_KEY environment variable is not set.")
                
                if reasoning == "medium":
                    self.model = "openai/gpt-6-luna"
                elif reasoning == "high":
                    self.model = "openai/gpt-6-luna"
                else:
                    raise ValueError("Invalid reasoning level. Choose 'medium' or 'high'.")
               
        

    def get_llm(self):
        return self.llm 
         