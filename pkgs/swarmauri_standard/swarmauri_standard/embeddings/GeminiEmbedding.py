from typing import List, Literal, Optional

import httpx
from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase
from swarmauri_base.ComponentBase import ComponentBase

from swarmauri_standard.vectors.Vector import Vector


@ComponentBase.register_type(EmbeddingBase, "GeminiEmbedding")
class GeminiEmbedding(EmbeddingBase):
    """
    A class for generating embeddings using the Google Gemini API via REST endpoints.

    This class allows users to obtain embeddings for text data using specified models
    from the Gemini API through direct HTTP requests.

    Attributes:
        model (str): The model to use for generating embeddings. Defaults to 'text-embedding-004'.
        allowed_models (List[str]): List of supported Gemini embedding models.
        allowed_task_types (List[str]): List of supported task types for embeddings.
        api_key (str): API key for authentication. Can be None for serialization.

    Raises:
        ValueError: If an invalid model or task type is provided during initialization.

    Example:
        >>> gemini_embedding = GeminiEmbedding(api_key='your_api_key', model='text-embedding-004')
        >>> embeddings = gemini_embedding.infer_vector(["Hello, world!", "Data science is awesome."])
    """

    type: Literal["GeminiEmbedding"] = "GeminiEmbedding"
    allowed_models: List[str] = ["text-embedding-004", "embedding-001"]
    allowed_task_types: List[str] = [
        "unspecified",
        "retrieval_query",
        "retrieval_document",
        "semantic_similarity",
        "classification",
        "clustering",
        "question_answering",
        "fact_verification",
    ]

    model: str = Field(default="text-embedding-004")
    api_key: Optional[SecretStr] = Field(default=None)
    task_type: str = Field(default="unspecified")
    output_dimensionality: Optional[int] = Field(default=None)

    _BASE_URL: str = PrivateAttr(
        default="https://generativelanguage.googleapis.com/v1beta"
    )
    _headers: dict = PrivateAttr(default_factory=dict)
    _client: httpx.Client = PrivateAttr(default_factory=httpx.Client)

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if self.model not in self.allowed_models:
            raise ValueError(
                f"Invalid model '{self.model}'. Allowed models are: {', '.join(self.allowed_models)}"
            )

        if self.task_type not in self.allowed_task_types:
            raise ValueError(
                f"Invalid task_type '{self.task_type}'. Allowed task types are: {', '.join(self.allowed_task_types)}"
            )

        if self.api_key.get_secret_value():
            self._headers = {
                "Content-Type": "application/json",
            }
            self._client = httpx.Client()

    def infer_vector(self, data: List[str]) -> List[Vector]:
        """
        Generate embeddings for the given list of strings.

        Args:
            data (List[str]): A list of strings to generate embeddings for.

        Returns:
            List[Vector]: A list of Vector objects containing the generated embeddings.

        Raises:
            ValueError: If an error occurs during the API request or response processing.
        """
        if not self.api_key.get_secret_value():
            raise ValueError("API key must be provided for inference")

        if not data:
            return []

        embeddings = []
        for text in data:
            payload = {
                "model": f"models/{self.model}",
                "content": {"parts": [{"text": text}]},
            }

            if self.task_type != "unspecified":
                payload["taskType"] = self.task_type
            if self.output_dimensionality:
                payload["outputDimensionality"] = self.output_dimensionality

            try:
                url = f"{self._BASE_URL}/models/{self.model}:embedContent?key={self.api_key.get_secret_value()}"
                response = self._client.post(
                    url, headers=self._headers, json=payload, timeout=30
                )
                response.raise_for_status()
                result = response.json()

                # Extract embedding from response
                embedding = result["embedding"]
                embeddings.append(Vector(value=embedding["values"]))

            except httpx.HTTPError as e:
                raise ValueError(f"Error calling Gemini AI API: {str(e)}")
            except (KeyError, ValueError) as e:
                raise ValueError(f"Error processing Gemini AI API response: {str(e)}")

        return embeddings

    def transform(self, data: List[str]) -> List[Vector]:
        """
        Transform a list of texts into embeddings.

        Args:
            data (List[str]): List of strings to transform into embeddings.

        Returns:
            List[Vector]: A list of vectors representing the transformed data.
        """
        return self.infer_vector(data)

    def save_model(self, path: str):
        raise NotImplementedError("save_model is not applicable for Gemini embeddings")

    def load_model(self, path: str):
        raise NotImplementedError("load_model is not applicable for Gemini embeddings")

    def fit(self, documents: List[str], labels=None):
        raise NotImplementedError("fit is not applicable for Gemini embeddings")

    def fit_transform(self, documents: List[str], **kwargs):
        raise NotImplementedError(
            "fit_transform is not applicable for Gemini embeddings"
        )

    def extract_features(self):
        raise NotImplementedError(
            "extract_features is not applicable for Gemini embeddings"
        )

    def __del__(self):
        """
        Clean up the httpx client when the instance is destroyed.
        """
        if hasattr(self, "_client"):
            self._client.close()
