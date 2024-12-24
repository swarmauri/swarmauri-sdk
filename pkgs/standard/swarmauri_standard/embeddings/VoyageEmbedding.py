import httpx
from typing import List, Literal, Any, Optional
from pydantic import PrivateAttr
from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase
from swarmauri_standard.vectors.Vector import Vector


class VoyageEmbedding(EmbeddingBase):
    """
    Class for embedding using VogageEmbedding

    LINK TO API KEY here: https://dash.voyageai.com/
    """

    allowed_models: List[str] = [
        "voyage-2",
        "voyage-large-2",
        "voyage-code-2",
        "voyage-lite-02-instruct",
    ]

    model: str = "voyage-2"
    type: Literal["VoyageEmbedding"] = "VoyageEmbedding"
    _BASE_URL: str = PrivateAttr(default="https://api.voyageai.com/v1/embeddings")
    _headers: dict = PrivateAttr()
    _client: httpx.Client = PrivateAttr()

    def __init__(self, api_key: str, model: str = "voyage-2", **kwargs):
        super().__init__(**kwargs)

        if model not in self.allowed_models:
            raise ValueError(
                f"Invalid model '{model}'. Allowed models are: {', '.join(self.allowed_models)}"
            )

        self.model = model

        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self._client = httpx.Client()

    def transform(self, data: List[str]) -> List[Vector]:
        """
        Transform a list of texts into embeddings using Voyage AI API.

        Args:
            data (List[str]): List of strings to transform into embeddings.

        Returns:
            List[Vector]: A list of vectors representing the transformed data.
        """
        if not data:
            return []

        # Prepare the request payload
        payload = {
            "input": data,
            "model": self.model,
        }

        try:
            response = self._client.post(
                self._BASE_URL, headers=self._headers, json=payload
            )
            response.raise_for_status()
            result = response.json()

            # Extract embeddings and convert to Vector objects
            embeddings = [Vector(value=item["embedding"]) for item in result["data"]]
            return embeddings

        except httpx.HTTPError as e:
            raise ValueError(f"Error calling Voyage AI API: {str(e)}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error processing Voyage AI API response: {str(e)}")

    def infer_vector(self, data: str) -> List[Vector]:
        """
        Convenience method for transforming a single data point.

        Args:
            data (str): Single text data to transform.

        Returns:
            List[Vector]: A vector representing the transformed single data point.
        """
        return self.transform([data])

    def save_model(self, path: str):
        raise NotImplementedError("save_model is not applicable for Voyage embeddings")

    def load_model(self, path: str) -> Any:
        raise NotImplementedError("load_model is not applicable for Voyage embeddings")

    def fit(self, documents: List[str], labels=None) -> None:
        raise NotImplementedError("fit is not applicable for Voyage embeddings")

    def fit_transform(self, documents: List[str], **kwargs) -> List[Vector]:
        raise NotImplementedError(
            "fit_transform is not applicable for Voyage embeddings"
        )

    def extract_features(self) -> List[Any]:
        raise NotImplementedError(
            "extract_features is not applicable for Voyage embeddings"
        )

    def __del__(self):
        """
        Clean up the httpx client when the instance is destroyed.
        """
        if hasattr(self, "_client"):
            self._client.close()
