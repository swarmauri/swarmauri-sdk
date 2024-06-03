from abc import ABC, abstractmethod

class ITool(ABC):

   
    @property
    @abstractmethod
    def description(self):
        pass

    @description.setter
    @abstractmethod
    def description(self, value) -> None:
        pass
    
    @property
    @abstractmethod
    def parameters(self):
        pass

    @parameters.setter
    @abstractmethod
    def parameters(self, value)  -> None:
        pass
    @abstractmethod
    def as_dict(self):
        pass

    @abstractmethod
    def to_json(obj):
        pass
        
    @abstractmethod
    def call(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @property
    def function(self):
        pass
