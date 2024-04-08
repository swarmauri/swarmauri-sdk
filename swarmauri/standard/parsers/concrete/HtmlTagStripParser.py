from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document
import html
import re

class HTMLTagStripParser(IParser):
    """
    A concrete parser that removes HTML tags and unescapes HTML content,
    leaving plain text.
    """

    def parse(self, data):
        """
        Strips HTML tags from input data and unescapes HTML content.
        
        Args:
            data (str): The HTML content to be parsed.
        
        Returns:
            List[IDocument]: A list containing a single IDocument instance of the stripped text.
        """

        # Ensure that input is a string
        if not isinstance(data, str):
            raise ValueError("HTMLTagStripParser expects input data to be of type str.")
        
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', data)  # Matches anything in < > and replaces it with empty string
        
        # Unescape HTML entities
        text = html.unescape(text)

        # Wrap the cleaned text into a Document and return it in a list
        document = Document(doc_id="1", content=text, metadata={"original_length": len(data)})
        
        return [document]