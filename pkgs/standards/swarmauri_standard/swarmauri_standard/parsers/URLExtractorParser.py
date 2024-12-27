import re
from urllib.parse import urlparse
from typing import List, Union, Any, Literal
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase

class URLExtractorParser(ParserBase):
    """
    A concrete implementation of IParser that extracts URLs from text.
    
    This parser scans the input text for any URLs and creates separate
    documents for each extracted URL. It utilizes regular expressions
    to identify URLs within the given text.
    """
    type: Literal['URLExtractorParser'] = 'URLExtractorParser'

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parse input data (string) and extract URLs, each URL is then represented as a document.
        
        Parameters:
        - data (Union[str, Any]): The input data to be parsed for URLs.
        
        Returns:
        - List[IDocument]: A list of documents, each representing an extracted URL.
        """
        if not isinstance(data, str):
            raise ValueError("URLExtractorParser expects input data to be of type str.")

        # Regular expression for finding URLs
        url_regex = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
        
        # Find all matches in the text
        urls = re.findall(url_regex, data)
        
        # Create a document for each extracted URL
        documents = [Document(content=url, metadata={"source": "URLExtractor"}) for i, url in enumerate(urls)]
        
        return documents