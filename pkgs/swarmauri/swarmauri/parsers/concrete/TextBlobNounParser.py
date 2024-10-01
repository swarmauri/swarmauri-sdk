from textblob import TextBlob
from typing import List, Union, Any, Literal
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase


class TextBlobNounParser(ParserBase):
    """
    A concrete implementation of IParser using TextBlob for Natural Language Processing tasks.

    This parser leverages TextBlob's functionalities such as noun phrase extraction,
    sentiment analysis, classification, language translation, and more for parsing texts.
    """

    type: Literal["TextBlobNounParser"] = "TextBlobNounParser"

    def __init__(self, **kwargs):
        import nltk

        nltk.download("punkt_tab")
        super().__init__(**kwargs)

    def parse(self, data: Union[str, Any]) -> List[Document]:
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
        document = Document(content=data, metadata={"noun_phrases": noun_phrases})

        return [document]
