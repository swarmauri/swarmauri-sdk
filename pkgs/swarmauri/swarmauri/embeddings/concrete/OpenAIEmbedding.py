import openai
from typing import List, Literal, Any
from pydantic import PrivateAttr
from swarmauri.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.vectors.concrete.Vector import Vector


class OpenAIEmbedding(EmbeddingBase):
    _allowed_models: List[str] = PrivateAttr(
        default=[
            "text-embedding-3-large",
            "text-embedding-3-small",
            "text-embedding-ada-002",
        ]
    )

    model: str = "text-embedding-3-small"
    type: Literal["OpenAIEmbedding"] = "OpenAIEmbedding"
    _client: openai.OpenAI = PrivateAttr()

    def __init__(
        self, api_key: str = None, model: str = "text-embedding-3-small", **kwargs
    ):
        super().__init__(**kwargs)

        if model not in self._allowed_models:
            raise ValueError(
                f"Invalid model '{model}'. Allowed models are: {', '.join(self._allowed_models)}"
            )

        self.model = model

        try:
            self._client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            raise ValueError(
                f"An error occurred while initializing OpenAI client: {str(e)}"
            )

    def transform(self, data: List[str]):
        """
        Transform data into embeddings using OpenAI API.

        Args:
            data (List[str]): List of strings to transform into embeddings.

        Returns:
            List[IVector]: A list of vectors representing the transformed data.
        """
        raise NotImplementedError("save_model is not applicable for OpenAI embeddings")

    def infer_vector(self, data: str):
        """
        Convenience method for transforming a single data point.

        Args:
            data (str): Single text data to transform.

        Returns:
            IVector: A vector representing the transformed single data point.
        """
        response = self._client.embeddings.create(input=data, model=self.model)
        embeddings = [Vector(value=item.embedding) for item in response.data]
        return embeddings

    def save_model(self, path: str):
        raise NotImplementedError("save_model is not applicable for OpenAI embeddings")

    def load_model(self, path: str) -> Any:
        raise NotImplementedError("load_model is not applicable for OpenAI embeddings")

    def fit(self, documents: List[str], labels=None) -> None:
        raise NotImplementedError("fit is not applicable for OpenAI embeddings")

    def fit_transform(self, documents: List[str], **kwargs) -> List[Vector]:
        raise NotImplementedError(
            "fit_transform is not applicable for OpenAI embeddings"
        )

    def extract_features(self) -> List[Any]:
        raise NotImplementedError(
            "extract_features is not applicable for OpenAI embeddings"
        )
