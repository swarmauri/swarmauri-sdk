from abc import ABC, abstractmethod

class ITool(ABC):
        
    @abstractmethod
    def call(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

