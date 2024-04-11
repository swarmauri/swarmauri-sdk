from abc import ABC, abstractmethod
from typing import Any, Dict

class IExportConf(ABC):
    """
    Interface for exporting configurations related to agent factories.
    
    Implementing classes are expected to provide functionality for representing
    the factory's configuration as a dictionary, JSON string, or exporting to a file.
    """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the agent factory's configuration to a dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the factory's configuration.
        """
        pass

    @abstractmethod
    def to_json(self) -> str:
        """
        Serializes the agent factory's configuration to a JSON string.
        
        Returns:
            str: A JSON string representation of the factory's configuration.
        """
        pass

    @abstractmethod
    def to_file(self, file_path: str) -> None:
        """
        Exports the agent factory's configuration to a file in a suitable format.
        
        Parameters:
            file_path (str): The path to the file where the configuration should be saved.
        """
        pass