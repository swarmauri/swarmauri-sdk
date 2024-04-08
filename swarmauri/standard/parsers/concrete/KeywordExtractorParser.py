import yake
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class KeywordExtractorParser(IParser):
    """
    Extracts keywords from text using the YAKE keyword extraction library.
    """

    def __init__(self, lang: str = 'en', num_keywords: int = 10):
        """
        Initialize the keyword extractor with specified language and number of keywords.

        Parameters:
        - lang (str): The language of the text for keyword extraction. Default is 'en' for English.
        - num_keywords (int): The number of top keywords to extract. Default is 10.
        """
        self.lang = lang
        self.num_keywords = num_keywords
        # Initialize YAKE extractor with specified parameters
        self.kw_extractor = yake.KeywordExtractor(lan=lang, n=3, dedupLim=0.9, dedupFunc='seqm', windowsSize=1, top=num_keywords, features=None)

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Extract keywords from input text and return as list of IDocument instances containing keyword information.

        Parameters:
        - data (Union[str, Any]): The input text from which to extract keywords.

        Returns:
        - List[IDocument]: A list of IDocument instances, each containing information about an extracted keyword.
        """
        # Ensure data is in string format for analysis
        text = str(data) if not isinstance(data, str) else data

        # Extract keywords using YAKE
        keywords = self.kw_extractor.extract_keywords(text)

        # Create Document instances for each keyword
        documents = [Document(doc_id=str(index), content=keyword, metadata={"score": score}) for index, (keyword, score) in enumerate(keywords)]
        
        return documents