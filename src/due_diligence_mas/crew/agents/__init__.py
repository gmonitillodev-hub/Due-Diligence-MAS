from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def get_agent(self):
        pass
    
    @abstractmethod
    def build_tasks(self):
        pass
    
    @abstractmethod
    def get_tasks(self):
        pass