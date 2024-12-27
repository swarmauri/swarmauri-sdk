"""
IDecAgentAPI: A dynamically generated Python package.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IDecAgentAPI(ABC):

    @abstractmethod
    def send_message(self, message: Dict[str, Any]) -> None:
        """
        Sends a message to the DecAgent.
        """
        pass
