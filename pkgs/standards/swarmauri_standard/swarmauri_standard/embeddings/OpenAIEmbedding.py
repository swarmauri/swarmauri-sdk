import httpx
from typing import List, Literal, Any, Optional
from pydantic import PrivateAttr, Field
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase


class OpenAIEmbedding(EmbeddingBase):
    """
    A class for generating embeddings using the OpenAI API via REST endpoints.

    This class allows users to obtain embeddings for text data using specified models
    from the OpenAI API through direct HTTP requests.

    Attributes:
        model (str): The model to use for generating embeddings. Defaults to 'text-embedding-3-small'.
        allowed_models (List[str]): List of supported OpenAI embedding models.
        api_key (str): API key for authentication. Can be None for serialization.

    Raises:
        ValueError: If an invalid model is provided during initialization or if the API request fails.

    Example:
        >>> openai_embedding = OpenAIEmbedding(api_key='your_api_key')
        >>> embeddings = openai_embedding.infer_vector(["Hello, world!", "Data science is awesome."])
    """

    type: Literal["OpenAIEmbedding"] = "OpenAIEmbedding"
    allowed_models: List[str] = [
        "text-embedding-3-large",
        "text-embedding-3-small",
        "text-embedding-ada-002",
    ]

    model: str = Field(default="text-embedding-3-small")
    api_key: Optional[str] = Field(default=None, exclude=True)

    _BASE_URL: str = PrivateAttr(default="https://api.openai.com/v1/embeddings")
    _headers: dict = PrivateAttr(default_factory=dict)
    _client: httpx.Client = PrivateAttr(default_factory=httpx.Client)

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        **kwargs,
    ):
        super().__init__(**kwargs)

        if model not in self.allowed_models:
            raise ValueError(
                f"Invalid model '{model}'. Allowed models are: {', '.join(self.allowed_models)}"
            )

        self.model = model
        self.api_key = api_key

        if api_key:
            self._headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
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

        try:
            payload = {
                "input": data,
                "model": self.model,
            }

            response = self._client.post(
                self._BASE_URL, headers=self._headers, json=payload, timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Extract embeddings and convert to Vector objects
            embeddings = [Vector(value=item["embedding"]) for item in result["data"]]
            return embeddings

        except httpx.HTTPError as e:
            raise ValueError(f"Error calling OpenAI API: {str(e)}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error processing OpenAI API response: {str(e)}")

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
        raise NotImplementedError("save_model is not applicable for OpenAI embeddings")

    def load_model(self, path: str):
        raise NotImplementedError("load_model is not applicable for OpenAI embeddings")

    def fit(self, documents: List[str], labels=None):
        raise NotImplementedError("fit is not applicable for OpenAI embeddings")

    def fit_transform(self, documents: List[str], **kwargs):
        raise NotImplementedError(
            "fit_transform is not applicable for OpenAI embeddings"
        )

    def extract_features(self):
        raise NotImplementedError(
            "extract_features is not applicable for OpenAI embeddings"
        )

    def __del__(self):
        """
        Clean up the httpx client when the instance is destroyed.
        """
        if hasattr(self, "_client"):
            self._client.close()
