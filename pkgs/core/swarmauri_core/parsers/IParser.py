from abc import ABC, abstractmethod
from typing import List, Union, Any

from swarmauri_core.documents.IDocument import IDocument
from typing_extensions import Annotated

FilePath = Annotated[str, "FilePath"]


class IParser(ABC):
    """
    Abstract base class for parsers. It defines a public method to parse input data (str or Message) into documents,
    and relies on subclasses to implement the specific parsing logic through protected and private methods.
    """

    @abstractmethod
    def parse(self, data: Union[str, bytes, FilePath]) -> List[IDocument]:
        """
        Public method to parse input data (either a str or a Message) into a list of Document instances.

        This method leverages the abstract _parse_data method which must be
        implemented by subclasses to define specific parsing logic.
        """
        pass
