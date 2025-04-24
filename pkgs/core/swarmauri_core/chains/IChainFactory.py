from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from swarmauri_core.chains.IChain import IChain
from swarmauri_core.chains.IChainStep import IChainStep


class IChainFactory(ABC):
    """
    Interface for creating and managing execution chains within the system.
    """

    @abstractmethod
    def create_chain(self, steps: Optional[List[IChainStep]] = None) -> IChain:
        pass

    @abstractmethod
    def get_chain(self) -> IChain:
        pass

    @abstractmethod
    def set_chain(self, chain: IChain) -> None:
        pass

    @abstractmethod
    def reset_chain(self) -> None:
        pass

    @abstractmethod
    def get_chain_steps(self) -> List[IChainStep]:
        pass

    @abstractmethod
    def set_chain_steps(self, steps: List[IChainStep]) -> None:
        pass

    @abstractmethod
    def add_chain_step(self, step: IChainStep) -> None:
        pass

    @abstractmethod
    def remove_chain_step(self, key: str) -> None:
        pass

    @abstractmethod
    def get_configs(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def set_configs(self, **configs) -> None:
        pass

    @abstractmethod
    def get_config(self, key: str) -> Any:
        pass

    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        pass
