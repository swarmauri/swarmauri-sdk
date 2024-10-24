from typing import List, Any, Optional, Literal
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from swarmauri.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.vectors.concrete.Vector import Vector


class Doc2VecEmbedding(EmbeddingBase):
    _model: Doc2Vec
    type: Literal["Doc2VecEmbedding"] = "Doc2VecEmbedding"

    def __init__(
        self,
        vector_size: int = 3000,  # Reduced size for better performance
        window: int = 10,
        min_count: int = 1,
        workers: int = 5,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._model = Doc2Vec(
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=workers,
        )

    def fit(self, documents: List[str], labels=None) -> None:
        tagged_data = [
            TaggedDocument(words=doc.split(), tags=[str(i)])
            for i, doc in enumerate(documents)
        ]

        # Check if the model already has a vocabulary built
        if len(self._model.wv) == 0:
            self._model.build_vocab(
                tagged_data
            )  # Build vocabulary if not already built
        else:
            self._model.build_vocab(
                tagged_data, update=True
            )  # Update the vocabulary if it exists

        self._model.train(
            tagged_data,
            total_examples=self._model.corpus_count,
            epochs=self._model.epochs,
        )

    def extract_features(self) -> List[Any]:
        return list(self._model.wv.key_to_index.keys())

    def infer_vector(self, data: str) -> Vector:
        words = data.split()
        # Check if words are known to the model's vocabulary
        known_words = [word for word in words if word in self._model.wv]

        if not known_words:
            # Return a zero-vector if all words are OOV
            vector = [0.0] * self._model.vector_size
        else:
            # Infer vector from known words
            vector = self._model.infer_vector(known_words)

        return Vector(value=vector)

    def transform(self, documents: List[str]) -> List[Vector]:
        return [self.infer_vector(doc) for doc in documents]

    def fit_transform(self, documents: List[str], **kwargs) -> List[Vector]:
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def save_model(self, path: str) -> None:
        self._model.save(path)

    def load_model(self, path: str) -> None:
        """
        Loads a Doc2Vec model from the specified path.
        """
        self._model = Doc2Vec.load(path)
