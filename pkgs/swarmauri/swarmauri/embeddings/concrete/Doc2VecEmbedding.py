from typing import List, Union, Any, Literal
from pydantic import PrivateAttr
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from swarmauri.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.vectors.concrete.Vector import Vector

class Doc2VecEmbedding(EmbeddingBase):
    _model = PrivateAttr()
    type: Literal['Doc2VecEmbedding'] = 'Doc2VecEmbedding'    

    def __init__(self, 
                 vector_size: int = 2000, 
                 window: int = 10,
                 min_count: int = 1,
                 workers: int = 5,
                 **kwargs):
        super().__init__(**kwargs)
        self._model = Doc2Vec(vector_size=vector_size, 
                              window=window, 
                              min_count=min_count, 
                              workers=workers)
        

    def extract_features(self) -> List[Any]:
        return list(self._model.wv.key_to_index.keys())

    def fit(self, documents: List[str], labels=None) -> None:
        tagged_data = [TaggedDocument(words=_d.split(), 
            tags=[str(i)]) for i, _d in enumerate(documents)]

        self._model.build_vocab(tagged_data)
        self._model.train(tagged_data, total_examples=self._model.corpus_count, epochs=self._model.epochs)

    def transform(self, documents: List[str]) -> List[Vector]:
        vectors = [self._model.infer_vector(doc.split()) for doc in documents]
        return [Vector(value=vector) for vector in vectors]

    def fit_transform(self, documents: List[str], **kwargs) -> List[Vector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: str) -> Vector:
        vector = self._model.infer_vector(data.split())
        return Vector(value=vector.squeeze().tolist())

    def save_model(self, path: str) -> None:
        """
        Saves the Doc2Vec model to the specified path.
        """
        self._model.save(path)
    
    def load_model(self, path: str) -> None:
        """
        Loads a Doc2Vec model from the specified path.
        """
        self._model = Doc2Vec.load(path)