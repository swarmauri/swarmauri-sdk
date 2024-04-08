import re
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class RegExParser(IParser):
    """
    A parser that uses a regular expression to extract information from text.
    """

    def __init__(self, pattern: str):
        """
        Initializes the RegExParser with a specific regular expression pattern.

        Parameters:
        - pattern (str): The regular expression pattern used for parsing the text.
        """
        self.pattern = pattern

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input data using the specified regular expression pattern and
        returns a list of IDocument instances containing the extracted information.

        Parameters:
        - data (Union[str, Any]): The input data to be parsed. It can be a string or any format 
                                   that the concrete implementation can handle.

        Returns:
        - List[IDocument]: A list of IDocument instances containing the parsed information.
        """
        # Ensure data is a string
        if not isinstance(data, str):
            data = str(data)

        # Use the regular expression pattern to find all matches in the text
        matches = re.findall(self.pattern, data)

        # Create a Document for each match and collect them into a list
        documents = [Document(doc_id=str(i+1), content=match, metadata={}) for i, match in enumerate(matches)]

        return documents