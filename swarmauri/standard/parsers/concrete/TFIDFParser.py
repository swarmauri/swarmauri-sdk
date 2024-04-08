from sklearn.feature_extraction.text import TfidfVectorizer
from swarmauri.core.parsers.IParser import IParser
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document

class TFIDFParser(IParser):
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        super().__init__()

    def parse(self, data):
        # Assuming `data` is a list of strings (documents)
        tfidf_matrix = self.vectorizer.fit_transform(data)
        # Depending on how you want to use the output, you could return Document objects
        # For demonstration, let's return a list of IDocument with vectorized content
        documents = [Document(doc_id=str(i), content=vector, metadata={}) for i, vector in enumerate(tfidf_matrix.toarray())]
        return documents