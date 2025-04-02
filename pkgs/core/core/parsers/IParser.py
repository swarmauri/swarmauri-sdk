from abc import ABC, abstractmethod

class IParser(ABC):
    """
    Abstract base class defining the interface for data parsing operations.
    Subclasses must implement all methods with appropriate type annotations.
    """
    
    @abstractmethod
    def dump(self, data: 'Data', file_path: str) -> None:
        """
        Serialize data to a file.
        
        Args:
            data: The data to serialize.
            file_path: Path to the output file.
        """
    
    @abstractmethod
    def dumps(self, data: 'Data') -> str:
        """
        Serialize data to a string.
        
        Args:
            data: The data to serialize.
        """
    
    @abstractmethod
    def load(self, file_path: str) -> 'Data':
        """
        Deserialize data from a file.
        
        Args:
            file_path: Path to the input file.
        """
    
    @abstractmethod
    def loads(self, data: str) -> 'Data':
        """
        Deserialize data from a string.
        
        Args:
            data: The string to deserialize.
        """
    
    @abstractmethod
    def round_trip_dump(self, data: 'Data', file_path: str) -> None:
        """
        Serialize data to a file and then deserialize it back to ensure consistency.
        
        Args:
            data: The data to serialize.
            file_path: Path to the output file.
        """
    
    @abstractmethod
    def round_trip_dumps(self, data: 'Data') -> str:
        """
        Serialize data to a string and then deserialize it back to ensure consistency.
        
        Args:
            data: The data to serialize.
        """
    
    @abstractmethod
    def round_trip_load(self, file_path: str) -> 'Data':
        """
        Deserialize data from a file and then serialize it back to ensure consistency.
        
        Args:
            file_path: Path to the input file.
        """
    
    @abstractmethod
    def round_trip_loads(self, data: str) -> 'Data':
        """
        Deserialize data from a string and then serialize it back to ensure consistency.
        
        Args:
            data: The string to deserialize.
        """