from abc import ABC
from typing import List
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.agents.IAgentRetrieve import IAgentRetrieve

class AgentRetrieveBase(IAgentRetrieve, ABC):

    def __init__(self):
        self._last_retrieved = []

    @property
    def last_retrieved(self) -> List[IDocument]:
        self._last_retrieved

    @last_retrieved.setter
    def last_retrieved(self, value: List[IDocument]) -> List[IDocument]:
        self._last_retrieved = value