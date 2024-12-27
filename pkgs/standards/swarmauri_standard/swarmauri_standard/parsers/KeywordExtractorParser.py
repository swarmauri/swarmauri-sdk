import yake
from typing import List, Union, Any, Literal
from pydantic import ConfigDict, PrivateAttr
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase

class KeywordExtractorParser(ParserBase):
    """
    Extracts keywords from text using the YAKE keyword extraction library.
    """
    lang: str = 'en'
    num_keywords: int = 10
    _kw_extractor: yake.KeywordExtractor = PrivateAttr(default=None)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['KeywordExtractorParser'] = 'KeywordExtractorParser'
    
    def __init__(self, **data):
        super().__init__(**data)
        self._kw_extractor = yake.KeywordExtractor(lan=self.lang,
                                                   n=3, 
                                                   dedupLim=0.9, 
                                                   dedupFunc='seqm', 
                                                   windowsSize=1, 
                                                   top=self.num_keywords, 
                                                   features=None)
    

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Extract keywords from input text and return as list of Document instances containing keyword information.

        Parameters:
        - data (Union[str, Any]): The input text from which to extract keywords.

        Returns:
        - List[Document]: A list of Document instances, each containing information about an extracted keyword.
        """
        # Ensure data is in string format for analysis
        text = str(data) if not isinstance(data, str) else data

        # Extract keywords using YAKE
        keywords = self._kw_extractor.extract_keywords(text)

        # Create Document instances for each keyword
        documents = [Document(content=keyword, metadata={"score": score}) for index, (keyword, score) in enumerate(keywords)]
        
        return documents