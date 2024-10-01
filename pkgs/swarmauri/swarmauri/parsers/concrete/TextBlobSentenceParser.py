from textblob import TextBlob
from typing import List, Union, Any, Literal
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase


class TextBlobSentenceParser(ParserBase):
    """
    A parser that leverages TextBlob to break text into sentences.

    This parser uses the natural language processing capabilities of TextBlob
    to accurately identify sentence boundaries within large blocks of text.
    """

    type: Literal["TextBlobSentenceParser"] = "TextBlobSentenceParser"

    def __init__(self, **kwargs):
        import nltk

        nltk.download("punkt_tab")
        super().__init__(**kwargs)

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input text into sentence-based document chunks using TextBlob.

        Args:
            data (Union[str, Any]): The input text to be parsed.

        Returns:
            List[IDocument]: A list of IDocument instances, each representing a sentence.
        """
        # Ensure the input is a string
        if not isinstance(data, str):
            data = str(data)

        # Utilize TextBlob for sentence tokenization
        blob = TextBlob(data)
        sentences = blob.sentences

        # Create a document instance for each sentence
        documents = [
            Document(
                content=str(sentence), metadata={"parser": "TextBlobSentenceParser"}
            )
            for index, sentence in enumerate(sentences)
        ]

        return documents
