import warnings

from abc import abstractmethod

from typing import Optional, Union, List, Any, Literal
from pydantic import Field

from swarmauri_core.chunkers.IChunker import IChunker
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_model()
class ChunkerBase(IChunker, ComponentBase):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.
    """

    resource: Optional[str] = Field(default=ResourceTypes.CHUNKER.value)
    type: Literal["ChunkerBase"] = "ChunkerBase"

    @abstractmethod
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[Any]:
        pass
