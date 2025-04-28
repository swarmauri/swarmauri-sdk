from typing import Any, Dict, List, Literal, Optional, Union

import httpx
from pydantic import PrivateAttr, SecretStr
from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase
from swarmauri_base.ComponentBase import ComponentBase

from swarmauri_standard.vectors.Vector import Vector


@ComponentBase.register_type(EmbeddingBase, "CohereEmbedding")
class CohereEmbedding(EmbeddingBase):
    """
    A class for generating embeddings using the Cohere REST API.

    This class provides an interface to generate embeddings for text and image data using various
    Cohere embedding models. It supports different task types, embedding types, and
    truncation options.

    Attributes:
        type (Literal["CohereEmbedding"]): The type identifier for this embedding class.
        model (str): The Cohere embedding model to use.
        api_key (SecretStr): The API key for accessing the Cohere API.
        allowed_task_types (List[str]): List of supported task types for embeddings

    Link to Allowed Models: https://docs.cohere.com/reference/embed
    Linke to API KEY: https://dashboard.cohere.com/api-keys
    """

    type: Literal["CohereEmbedding"] = "CohereEmbedding"

    allowed_models: List[str] = [
        "embed-english-v3.0",
        "embed-multilingual-v3.0",
        "embed-english-light-v3.0",
        "embed-multilingual-light-v3.0",
        "embed-english-v2.0",
        "embed-english-light-v2.0",
        "embed-multilingual-v2.0",
    ]

    # Private attributes
    _BASE_URL: str = PrivateAttr(default="https://api.cohere.com/v2")
    allowed_task_types: List[str] = [
        "search_document",
        "search_query",
        "classification",
        "clustering",
        "image",
    ]

    _allowed_embedding_types: List[str] = PrivateAttr(
        default=["float", "int8", "uint8", "binary", "ubinary"]
    )

    # Public attributes
    model: str = "embed-english-v3.0"
    api_key: SecretStr = None
    task_type: str = "search_document"
    embedding_types: Optional[str] = "float"
    truncate: Optional[str] = "END"

    # Private configuration attributes
    _client: httpx.Client = PrivateAttr()

    def __init__(
        self,
        **kwargs: Dict[str, Any],
    ):
        """
        Initialize the CohereEmbedding instance.

        Args:
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If any of the input parameters are invalid.
        """
        super().__init__(**kwargs)

        if self.model not in self.allowed_models:
            raise ValueError(
                f"Invalid model '{self.model}'. Allowed models are: {', '.join(self.allowed_models)}"
            )

        if self.task_type not in self.allowed_task_types:
            raise ValueError(
                f"Invalid task_type '{self.task_type}'. Allowed task types are: {', '.join(self.allowed_task_types)}"
            )
        if self.embedding_types not in self._allowed_embedding_types:
            raise ValueError(
                f"Invalid embedding_types '{self.embedding_types}'. Allowed embedding types are: {', '.join(self._allowed_embedding_types)}"
            )
        if self.truncate not in ["END", "START", "NONE"]:
            raise ValueError(
                f"Invalid truncate '{self.truncate}'. Allowed truncate are: END, START, NONE"
            )
        self._client = httpx.Client()

    def _make_request(self, payload: dict) -> dict:
        """
        Make a request to the Cohere API.

        Args:
            payload (dict): The request payload.

        Returns:
            dict: The API response.

        Raises:
            RuntimeError: If the API request fails.
        """
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
        }
        try:
            response = self._client.post(
                f"{self._BASE_URL}/embed", headers=headers, json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"API request failed: {str(e)}")

    def infer_vector(self, data: Union[List[str], List[str]]) -> List[Vector]:
        """
        Generate embeddings for the given list of texts or images.

        Args:
            data (Union[List[str], List[str]]): A list of texts or base64-encoded images.

        Returns:
            List[Vector]: A list of Vector objects containing the generated embeddings.

        Raises:
            RuntimeError: If an error occurs during the embedding generation process.
        """
        try:
            # Prepare the payload based on input type
            payload = {
                "model": self.model,
                "embedding_types": [self.embedding_types],
            }

            if self.task_type == "image":
                payload["input_type"] = "image"
                payload["images"] = data
            else:
                payload["input_type"] = self.task_type
                payload["texts"] = data
                payload["truncate"] = self.truncate

            # Make the API request
            response = self._make_request(payload)

            # Extract embeddings from response
            embeddings = response["embeddings"][self.embedding_types]
            return [Vector(value=item) for item in embeddings]

        except Exception as e:
            raise RuntimeError(
                f"An error occurred during embedding generation: {str(e)}"
            )

    def __del__(self):
        """
        Clean up the httpx client when the instance is destroyed.
        """
        if hasattr(self, "_client"):
            self._client.close()

    def save_model(self, path: str):
        raise NotImplementedError("save_model is not applicable for Cohere embeddings")

    def load_model(self, path: str):
        raise NotImplementedError("load_model is not applicable for Cohere embeddings")

    def fit(self, documents: List[str], labels=None):
        raise NotImplementedError("fit is not applicable for Cohere embeddings")

    def transform(self, data: List[str]):
        raise NotImplementedError("transform is not applicable for Cohere embeddings")

    def fit_transform(self, documents: List[str], **kwargs):
        raise NotImplementedError(
            "fit_transform is not applicable for Cohere embeddings"
        )

    def extract_features(self):
        raise NotImplementedError(
            "extract_features is not applicable for Cohere embeddings"
        )
