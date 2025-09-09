from abc import abstractmethod
from typing import Any, List, Literal, Optional, TypeVar, Union

from pydantic import Field
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.parsers.IParser import IParser

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

T = TypeVar("T", bound=IDocument)


@ComponentBase.register_model()
class ParserBase(IParser, ComponentBase):
    """
    Parse input data into ``Document`` objects.

    This interface defines abstract methods that convert raw input into
    ``Document`` instances. Implementing classes should override these
    methods with parsing logic suited to their specific needs.
    """

    resource: Optional[str] = Field(default=ResourceTypes.PARSER.value, frozen=True)
    type: Literal["ParserBase"] = "ParserBase"

    @abstractmethod
    def parse(self, data: Union[str, Any]) -> List[T]:
        """
        Public method to parse input data (either a str or a Message) into a list of Document instances.

        This method leverages the abstract _parse_data method which must be
        implemented by subclasses to define specific parsing logic.
        """
        pass
