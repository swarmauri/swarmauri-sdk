from typing import List, Union, Any
from textblob import TextBlob
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class TextBlobNounParser(IParser):
    """
    A concrete implementation of IParser using TextBlob for Natural Language Processing tasks.
    
    This parser leverages TextBlob's functionalities such as noun phrase extraction, 
    sentiment analysis, classification, language translation, and more for parsing texts.
    """
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input data using TextBlob to perform basic NLP tasks 
        and returns a list of documents with the parsed information.
        
        Parameters:
        - data (Union[str, Any]): The input data to parse, expected to be text data for this parser.
        
        Returns:
        - List[IDocument]: A list of documents with metadata generated from the parsing process.
        """
        # Ensure the data is a string
        if not isinstance(data, str):
            raise ValueError("TextBlobParser expects a string as input data.")
        
        # Use TextBlob for NLP tasks
        blob = TextBlob(data)
        
        # Extracts noun phrases to demonstrate one of TextBlob's capabilities. 
        # In practice, this parser could be expanded to include more sophisticated processing.
        noun_phrases = list(blob.noun_phrases)
        
        # Example: Wrap the extracted noun phrases into an IDocument instance
        # In real scenarios, you might want to include more details, like sentiment, POS tags, etc.
        document = Document(doc_id="0", content=data, metadata={"noun_phrases": noun_phrases})
        
        return [document]