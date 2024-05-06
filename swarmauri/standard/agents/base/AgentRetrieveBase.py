from abc import ABC
from swarmauri.core.agents.IAgentRetrieve import IAgentRetrieve
from swarmauri.core.documents.IDocument import IDocument

class AgentRetrieveBase(IAgentRetrieve, ABC):
    self._last_retrieved = []

    @property
    def last_retrieved(self) -> List[IDocument]:
        self._last_retrieved

    @last_retrieved.setter
    def last_retrieved(self, value: List[IDocument]) -> List[IDocument]:
        self._last_retrieved = value