import re
from typing import List, Union, Any, Literal
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase

class PhoneNumberExtractorParser(ParserBase):
    """
    A parser that extracts phone numbers from the input text.
    Utilizes regular expressions to identify phone numbers in various formats.
    """
    type: Literal['PhoneNumberExtractorParser'] = 'PhoneNumberExtractorParser'
    
    def parse(self, data: Union[str, Any]) -> List[Document]:
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
        documents = [Document(content=phone_number, metadata={}) for index, phone_number in enumerate(phone_numbers)]

        return documents