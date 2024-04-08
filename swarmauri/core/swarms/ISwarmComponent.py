from abc import ABC, abstractmethod

class ISwarmComponent(ABC):
    """
    Interface for defining a general component within a swarm system.
    """

    @abstractmethod
    def __init__(self, key: str, name: str):
        """
        Initializes a swarm component with a unique key and name.
        """
        pass