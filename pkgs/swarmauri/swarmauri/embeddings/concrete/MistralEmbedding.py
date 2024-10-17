import logging

import mistralai
from typing import List, Literal, Any
from pydantic import PrivateAttr
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.embeddings.base.EmbeddingBase import EmbeddingBase


class MistralEmbedding(EmbeddingBase):
    """
    A class for generating embeddings using the Mistral API.

    This class allows users to obtain embeddings for text data using specified models
    from the Mistral API.

    Attributes:
        model (str): The model to use for generating embeddings. Defaults to 'mistral-embed'.
        api_key (str): API key for authenticating requests to the Mistral API.

    Raises:
        ValueError: If an invalid model or task type is provided during initialization.

    Example:
        >>> mistral_embedding = MistralEmbedding(api_key='your_api_key', model='mistral_embed')
        >>> embeddings = mistral_embedding.infer_vector(["Hello, world!", "Data science is awesome."])
    """

    type: Literal["MistralEmbedding"] = "MistralEmbedding"

    _allowed_models: List[str] = PrivateAttr(default=["mistral-embed"])

    model: str = "mistral-embed"
    api_key: str = None
    _client: Any = PrivateAttr()

    def __init__(
        self,
        api_key: str = None,
        model: str = "mistral-embed",
        **kwargs,
    ):
        super().__init__(**kwargs)

        if model not in self._allowed_models:
            raise ValueError(
                f"Invalid model '{model}'. Allowed models are: {', '.join(self._allowed_models)}"
            )

        self.model = model
        self._client = mistralai.Mistral(api_key=api_key)
        logging.info("Testing")
        if not isinstance(self._client, mistralai.Mistral):
            raise ValueError("client must be an instance of mistralai.Mistral")

    def infer_vector(self, data: List[str]) -> List[Vector]:
        """
        Generate embeddings for the given list of strings.

        Args:
            data (List[str]): A list of strings to generate embeddings for.

        Returns:
            List[Vector]: A list of Vector objects containing the generated embeddings.

        Raises:
            RuntimeError: If an error occurs during the embedding generation process.
        """

        try:

            response = self._client.embeddings.create(
                model=self.model,
                inputs=data,
            )

            embeddings = [Vector(value=item.embedding) for item in response.data]
            return embeddings

        except Exception as e:
            raise RuntimeError(
                f"An error occurred during embedding generation: {str(e)}"
            )

    def save_model(self, path: str):
        raise NotImplementedError("save_model is not applicable for Mistral embeddings")

    def load_model(self, path: str):
        raise NotImplementedError("load_model is not applicable for Mistral embeddings")

    def fit(self, documents: List[str], labels=None):
        raise NotImplementedError("fit is not applicable for Mistral embeddings")

    def transform(self, data: List[str]):
        raise NotImplementedError("transform is not applicable for Mistral embeddings")

    def fit_transform(self, documents: List[str], **kwargs):
        raise NotImplementedError(
            "fit_transform is not applicable for Mistral embeddings"
        )

    def extract_features(self):
        raise NotImplementedError(
            "extract_features is not applicable for Mistral embeddings"
        )
