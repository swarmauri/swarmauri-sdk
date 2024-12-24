from abc import ABC, abstractmethod
from typing import Optional, Union, List, Any, Literal
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes

class ChunkerBase(ComponentBase, ABC):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.CHUNKER.value)
    type: Literal['ChunkerBase'] = 'ChunkerBase'
    
    @abstractmethod
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[Any]:
        pass