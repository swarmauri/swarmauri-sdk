from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

class IAgent(ABC):

    @abstractmethod
    def exec(self, input_data: Optional[Any], llm_kwargs: Optional[Dict]) -> Any:
        """
        Executive method that triggers the agent's action based on the input data.
        """
        pass
    