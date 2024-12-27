from bs4 import BeautifulSoup
from typing import List, Union, Any, Literal
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase

class BeautifulSoupElementParser(ParserBase):
    """
    A concrete parser that leverages BeautifulSoup to extract specific HTML elements and their content.
    """
    element: str
    type: Literal['BeautifulSoupElementParser'] = 'BeautifulSoupElementParser'

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input data to extract specific HTML elements.

        Args:
            data (Union[str, Any]): The HTML content to be parsed.

        Returns:
            List[IDocument]: A list of documents containing the extracted elements.
        """
        # Ensure that input is a string
        if not isinstance(data, str):
            raise ValueError("BeautifulSoupElementParser expects input data to be of type str.")
        
        # Initialize BeautifulSoup parser
        soup = BeautifulSoup(data, 'html.parser')
        
        # Find all specified elements
        elements = soup.find_all(self.element)
        
        # Create a document for each element
        documents = [
            Document(
                content=str(element),
                metadata={"element": self.element, "index": index}
            ) 
            for index, element in enumerate(elements)
        ]
        
        return documents