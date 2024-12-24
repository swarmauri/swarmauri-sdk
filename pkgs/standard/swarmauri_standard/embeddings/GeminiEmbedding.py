import httpx
from typing import List, Literal, Any, Optional
from pydantic import PrivateAttr, Field
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase


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
    api_key: Optional[str] = Field(default=None, exclude=True)

    _BASE_URL: str = PrivateAttr(
        default="https://generativelanguage.googleapis.com/v1beta"
    )
    _headers: dict = PrivateAttr(default_factory=dict)
    _client: httpx.Client = PrivateAttr(default_factory=httpx.Client)
    _task_type: str = PrivateAttr(default="unspecified")
    _output_dimensionality: int = PrivateAttr(default=None)

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-004",
        task_type: Optional[str] = "unspecified",
        output_dimensionality: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if model not in self.allowed_models:
            raise ValueError(
                f"Invalid model '{model}'. Allowed models are: {', '.join(self.allowed_models)}"
            )

        if task_type not in self.allowed_task_types:
            raise ValueError(
                f"Invalid task_type '{task_type}'. Allowed task types are: {', '.join(self.allowed_task_types)}"
            )

        self.model = model
        self.api_key = api_key
        self._task_type = task_type
        self._output_dimensionality = output_dimensionality

        if api_key:
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
        if not self.api_key:
            raise ValueError("API key must be provided for inference")

        if not data:
            return []

        embeddings = []
        for text in data:
            payload = {
                "model": f"models/{self.model}",
                "content": {"parts": [{"text": text}]},
            }

            if self._task_type != "unspecified":
                payload["taskType"] = self._task_type
            if self._output_dimensionality:
                payload["outputDimensionality"] = self._output_dimensionality

            try:
                url = f"{self._BASE_URL}/models/{self.model}:embedContent?key={self.api_key}"
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
