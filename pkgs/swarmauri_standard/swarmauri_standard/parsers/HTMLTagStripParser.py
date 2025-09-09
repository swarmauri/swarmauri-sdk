import html
import re
from typing import List, Literal
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ParserBase, "HTMLTagStripParser")
class HTMLTagStripParser(ParserBase):
    """
    A concrete parser that removes HTML tags and unescapes HTML content,
    leaving plain text.
    """

    type: Literal["HTMLTagStripParser"] = "HTMLTagStripParser"

    def parse(self, data: str) -> List[Document]:
        """
        Strips HTML tags from input data and unescapes HTML content.

        Args:
            data (str): The HTML content to be parsed.

        Returns:
            List[Document]: A list containing a single IDocument instance of the stripped text.
        """

        # Ensure that input is a string
        if not isinstance(data, str):
            raise ValueError("HTMLTagStripParser expects input data to be of type str.")

        # Remove HTML tags
        text = re.sub(
            "<[^<]+?>", "", data
        )  # Matches anything in < > and replaces it with empty string

        # Unescape HTML entities
        text = html.unescape(text)

        # Wrap the cleaned text into a Document and return it in a list
        document = Document(content=text, metadata={"original_length": len(data)})

        return [document]
