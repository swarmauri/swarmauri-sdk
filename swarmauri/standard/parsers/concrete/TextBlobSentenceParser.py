from textblob import TextBlob
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document
from typing import List, Union, Any

class TextBlobParser(IParser):
    """
    A parser that leverages TextBlob to break text into sentences.

    This parser uses the natural language processing capabilities of TextBlob
    to accurately identify sentence boundaries within large blocks of text.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
            Document(doc_id=str(index), content=str(sentence), metadata={'parser': 'TextBlobParser'})
            for index, sentence in enumerate(sentences)
        ]

        return documents