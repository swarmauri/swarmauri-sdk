from textblob import TextBlob
from typing import List, Union, Any, Literal
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ParserBase, "TextBlobNounParser")
class TextBlobNounParser(ParserBase):
    """
    A concrete implementation of IParser using TextBlob for Natural Language Processing tasks.

    This parser leverages TextBlob's functionalities such as noun phrase extraction,
    sentiment analysis, classification, language translation, and more for parsing texts.
    """

    type: Literal["TextBlobNounParser"] = "TextBlobNounParser"

    def __init__(self, **kwargs):
        try:
            import nltk

            # Download required NLTK data
            nltk.download("punkt")
            nltk.download("averaged_perceptron_tagger")
            nltk.download("brown")
            nltk.download("wordnet")
            nltk.download("punkt_tab")
            super().__init__(**kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize NLTK resources: {str(e)}")

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

        try:
            # Use TextBlob for NLP tasks
            blob = TextBlob(data)

            # Extracts noun phrases to demonstrate one of TextBlob's capabilities.
            noun_phrases = list(blob.noun_phrases)

            # Create document with extracted information
            document = Document(content=data, metadata={"noun_phrases": noun_phrases})

            return [document]
        except Exception as e:
            raise RuntimeError(f"Error during text parsing: {str(e)}")
