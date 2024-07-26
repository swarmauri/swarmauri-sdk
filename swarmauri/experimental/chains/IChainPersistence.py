from abc import ABC, abstractmethod
from typing import Dict, Any
from swarmauri.core.chains.IChain import IChain

class IChainPersistence(ABC):
    @abstractmethod
    def save_state(self, chain: IChain, state: Dict[str, Any]) -> None:
        """Save the state of the given chain."""
        pass

    @abstractmethod
    def load_state(self, chain_id: str) -> Dict[str, Any]:
        """Load the state of a chain by its identifier."""
        pass