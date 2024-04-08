import re
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class PhoneNumberExtractorParser(IParser):
    """
    A parser that extracts phone numbers from the input text.
    Utilizes regular expressions to identify phone numbers in various formats.
    """

    def __init__(self):
        """
        Initializes the PhoneNumberExtractorParser.
        """
        super().__init__()

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input data, looking for phone numbers employing a regular expression.
        Each phone number found is contained in a separate IDocument instance.

        Parameters:
        - data (Union[str, Any]): The input text to be parsed for phone numbers.

        Returns:
        - List[IDocument]: A list of IDocument instances, each containing a phone number.
        """
        # Define a regular expression for phone numbers.
        # This is a simple example and might not capture all phone number formats accurately.
        phone_regex = r'\+?\d[\d -]{8,}\d'

        # Find all occurrences of phone numbers in the text
        phone_numbers = re.findall(phone_regex, str(data))

        # Create a new IDocument for each phone number found
        documents = [Document(doc_id=str(index), content=phone_number, metadata={}) for index, phone_number in enumerate(phone_numbers)]

        return documents