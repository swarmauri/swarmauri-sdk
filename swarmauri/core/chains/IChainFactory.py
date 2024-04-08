from abc import ABC, abstractmethod
from subprocess import ABOVE_NORMAL_PRIORITY_CLASS
from typing import List, Any, Dict
from swarmauri.core.chains.IChain import IChain
from swarmauri.core.chains.IChainStep import IChainStep
from swarmauri.experimental.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.experimental.chains.IChainProcessingStrategy import IChainProcessingStrategy

class IChainFactory(ABC):
    """
    Interface for creating and managing execution chains within the system.
    """

    @abstractmethod
    def __init__(self, order_strategy: IChainOrderStrategy, processing_strategy: IChainProcessingStrategy, **configs):
        pass

    @abstractmethod
    def create_chain(self, steps: List[IChainStep] = None) -> IChain:
        pass
    
    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_chain_info(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_chain(self) -> IChain:
        pass
    
    @abstractmethod
    def set_chain(self, chain: IChain):
        pass
    
    @abstractmethod
    def reset_chain(self):
        pass
    
    @abstractmethod
    def get_chain_steps(self) -> List[IChainStep]:
        pass
    
    @abstractmethod
    def set_chain_steps(self, steps: List[IChainStep]):
        pass
    
    @abstractmethod
    def add_chain_step(self, step: IChainStep):
        pass
    
    @abstractmethod
    def remove_chain_step(self, key: str):
        pass
    
    @abstractmethod
    def get_chain_order_strategy(self) -> IChainOrderStrategy:
        pass
    
    @abstractmethod
    def set_chain_order_strategy(self, order_strategy: IChainOrderStrategy):
        pass
    
    @abstractmethod
    def get_chain_processing_strategy(self) -> IChainProcessingStrategy:
        pass
    
    @abstractmethod
    def set_chain_processing_strategy(self, processing_strategy: IChainProcessingStrategy):
        pass
    
    @abstractmethod
    def get_configs(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def set_configs(self, **configs):
        pass
    
    @abstractmethod
    
    def get_config(self, key: str) -> Any:
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any):
        pass
    
    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_chain_info(self) -> Dict[str, Any]:
        pass    
    
