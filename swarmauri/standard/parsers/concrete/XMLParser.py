import xml.etree.ElementTree as ET
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class XMLParser(IParser):
    """
    A parser that extracts information from XML data and converts it into IDocument objects.
    This parser assumes a simple use-case where each targeted XML element represents a separate document.
    """

    def __init__(self, element_tag: str):
        """
        Initialize the XMLParser with the tag name of the XML elements to be extracted as documents.

        Parameters:
        - element_tag (str): The tag name of XML elements to parse into documents.
        """
        self.element_tag = element_tag

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
            doc = Document(doc_id=None, content=content, metadata=metadata)
            documents.append(doc)

        return documents