from abc import ABC, abstractmethod
from due_diligence_mas.mas_definition.constants.common import Framework


class BaseAgent(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def get_agent(self):
        pass
    
    @abstractmethod
    def build_tasks(self, topic: str = "", context: list = []):
        pass
    
    @abstractmethod
    def get_tasks(self):
        pass
    
class CrewAI_Agent(BaseAgent):
    pass

class LangGraph_Agent(BaseAgent):
    pass

class AgentFactory:
    
    @staticmethod
    def create(framework: str) -> CrewAI_Agent | LangGraph_Agent:
        
        match framework.lower():
            
            case Framework.LANG_GRAPH.value:
                return LangGraph_Agent