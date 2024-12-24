import xml.etree.ElementTree as ET
from typing import List, Union, Any, Literal

from pydantic import Field
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase

class XMLParser(ParserBase):
    """
    A parser that extracts information from XML data and converts it into IDocument objects.
    This parser assumes a simple use-case where each targeted XML element represents a separate document.
    """
    element_tag: str = Field(default="root")
    type: Literal['XMLParser'] = 'XMLParser'

    
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses XML data and converts elements with the specified tag into IDocument instances.

        Parameters:
        - data (Union[str, Any]): The XML data as a string to be parsed.

        Returns:
        - List[IDocument]: A list of IDocument instances created from the XML elements.
        """
        if isinstance(data, str):
            root = ET.fromstring(data)  # Parse the XML string into an ElementTree element
        else:
            raise TypeError("Data for XMLParser must be a string containing valid XML.")

        documents = []
        for element in root.findall(self.element_tag):
            # Extracting content and metadata from each element
            content = "".join(element.itertext())  # Get text content
            metadata = {child.tag: child.text for child in element}  # Extract child elements as metadata

            # Create a Document instance for each element
            doc = Document(content=content, metadata=metadata)
            documents.append(doc)

        return documents