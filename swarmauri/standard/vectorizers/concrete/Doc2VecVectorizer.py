from typing import List, Union, Any
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.core.vectorizers.ISaveModel import ISaveModel

class Doc2VecVectorizer(IVectorize, IFeature, ISaveModel):
    def __init__(self):
        self.model = Doc2Vec(vector_size=2000, window=10, min_count=1, workers=5)

    def extract_features(self):
        return list(self.model.wv.key_to_index.keys())

    def fit(self, documents: List[str], labels=None) -> None:
        tagged_data = [TaggedDocument(words=_d.split(), 
            tags=[str(i)]) for i, _d in enumerate(documents)]

        self.model.build_vocab(tagged_data)
        self.model.train(tagged_data, total_examples=self.model.corpus_count, epochs=self.model.epochs)

    def transform(self, documents: List[str]) -> List[IVector]:
        vectors = [self.model.infer_vector(doc.split()) for doc in documents]
        return [SimpleVector(vector) for vector in vectors]

    def fit_transform(self, documents: List[Union[str, Any]], **kwargs) -> List[IVector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: str) -> IVector:
        vector = self.model.infer_vector(data.split())
        return SimpleVector(vector.squeeze().tolist())

    def save_model(self, path: str) -> None:
        """
        Saves the Doc2Vec model to the specified path.
        """
        self.model.save(path)
    
    def load_model(self, path: str) -> None:
        """
        Loads a Doc2Vec model from the specified path.
        """
        self.model = Doc2Vec.load(path)