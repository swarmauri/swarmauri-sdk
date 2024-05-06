from abc import ABC, abstractmethod

class IAgentSystemContext(ABC):
    
    @property
    @abstractmethod
    def system_context(self):
        pass

    @system_context.setter
    @abstractmethod
    def system_context(self):
        pass