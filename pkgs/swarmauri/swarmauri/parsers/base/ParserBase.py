from abc import ABC, abstractmethod
from typing import Optional, Union, List, Any, Literal
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.parsers.IParser import IParser


class ParserBase(IParser, ComponentBase):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.PARSER.value)
    type: Literal['ParserBase'] = 'ParserBase'
    
    @abstractmethod
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Public method to parse input data (either a str or a Message) into a list of Document instances.
        
        This method leverages the abstract _parse_data method which must be
        implemented by subclasses to define specific parsing logic.
        """
        pass