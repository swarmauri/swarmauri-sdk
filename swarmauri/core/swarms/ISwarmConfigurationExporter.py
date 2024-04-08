from abc import ABC, abstractmethod
from typing import Dict
class ISwarmConfigurationExporter(ABC):

    @abstractmethod
    def to_dict(self) -> Dict:
        """
        Serializes the swarm configuration to a dictionary.

        Returns:
            Dict: The serialized configuration as a dictionary.
        """
        pass

    @abstractmethod
    def to_json(self) -> str:
        """
        Serializes the swarm configuration to a JSON string.

        Returns:
            str: The serialized configuration as a JSON string.
        """
        pass

    @abstractmethod
    def to_pickle(self) -> bytes:
        """
        Serializes the swarm configuration to a Pickle byte stream.

        Returns:
            bytes: The serialized configuration as a Pickle byte stream.
        """
        pass