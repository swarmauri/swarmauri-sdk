from abc import ABC
from typing import List
from dataclasses import dataclass
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.agents.IAgentRetrieve import IAgentRetrieve

@dataclass
class AgentRetrieveBase(IAgentRetrieve, ABC):
    _last_retrieved: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if type(self.last_retrieved) == property:
            self.last_retrieved = []
        
    @property
    def last_retrieved(self) -> List[IDocument]:
        return self._last_retrieved

    @last_retrieved.setter
    def last_retrieved(self, value: List[IDocument]) -> None:
        self._last_retrieved = value