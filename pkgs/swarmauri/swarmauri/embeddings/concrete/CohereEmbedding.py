import cohere
from typing import List, Literal, Any, Optional
from pydantic import PrivateAttr
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.embeddings.base.EmbeddingBase import EmbeddingBase


class CohereEmbedding(EmbeddingBase):
    """
    A class for generating embeddings using the Cohere API.

    This class provides an interface to generate embeddings for text data using various
    Cohere embedding models. It supports different task types, embedding types, and
    truncation options.

    Attributes:
        type (Literal["CohereEmbedding"]): The type identifier for this embedding class.
        model (str): The Cohere embedding model to use.
        api_key (str): The API key for accessing the Cohere API.
    """

    type: Literal["CohereEmbedding"] = "CohereEmbedding"

    _allowed_models: List[str] = PrivateAttr(
        default=[
            "embed-english-v3.0",
            "embed-multilingual-v3.0",
            "embed-english-light-v3.0",
            "embed-multilingual-light-v3.0",
            "embed-english-v2.0",
            "embed-english-light-v2.0",
            "embed-multilingual-v2.0",
        ]
    )
    _allowed_task_types: List[str] = PrivateAttr(
        default=["search_document", "search_query", "classification", "clustering"]
    )
    _allowed_embedding_types: List[str] = PrivateAttr(
        default=["float", "int8", "uint8", "binary", "ubinary"]
    )

    model: str = "embed-english-v3.0"
    api_key: str = None
    _task_type: str = PrivateAttr("search_document")
    _embedding_types: Optional[str] = PrivateAttr("float")
    _truncate: Optional[str] = PrivateAttr("END")
    _client: cohere.Client = PrivateAttr()

    def __init__(
        self,
        api_key: str = None,
        model: str = "embed-english-v3.0",
        task_type: Optional[str] = "search_document",
        embedding_types: Optional[str] = "float",
        truncate: Optional[str] = "END",
        **kwargs,
    ):
        """
        Initialize the CohereEmbedding instance.

        Args:
            api_key (str, optional): The API key for accessing the Cohere API.
            model (str, optional): The Cohere embedding model to use. Defaults to "embed-english-v3.0".
            task_type (str, optional): The type of task for which embeddings are generated. Defaults to "search_document".
            embedding_types (str, optional): The type of embedding to generate. Defaults to "float".
            truncate (str, optional): The truncation strategy to use. Defaults to "END".
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If any of the input parameters are invalid.
        """
        super().__init__(**kwargs)

        if model not in self._allowed_models:
            raise ValueError(
                f"Invalid model '{model}'. Allowed models are: {', '.join(self._allowed_models)}"
            )

        if task_type not in self._allowed_task_types:
            raise ValueError(
                f"Invalid task_type '{task_type}'. Allowed task types are: {', '.join(self._allowed_task_types)}"
            )
        if embedding_types not in self._allowed_embedding_types:
            raise ValueError(
                f"Invalid embedding_types '{embedding_types}'. Allowed embedding types are: {', '.join(self._allowed_embedding_types)}"
            )
        if truncate not in ["END", "START", "NONE"]:
            raise ValueError(
                f"Invalid truncate '{truncate}'. Allowed truncate are: END, START, NONE"
            )

        self.model = model
        self._task_type = task_type
        self._embedding_types = embedding_types
        self._truncate = truncate
        self._client = cohere.Client(api_key=api_key)

    def infer_vector(self, data: List[str]) -> List[Vector]:
        """
        Generate embeddings for the given list of texts.

        Args:
            data (List[str]): A list of texts to generate embeddings for.

        Returns:
            List[Vector]: A list of Vector objects containing the generated embeddings.

        Raises:
            RuntimeError: If an error occurs during the embedding generation process.
        """

        try:
            response = self._client.embed(
                model=self.model,
                texts=data,
                input_type=self._task_type,
                embedding_types=[self._embedding_types],
                truncate=self._truncate,
            )
            embeddings_attr = getattr(response.embeddings, self._embedding_types)
            embeddings = [Vector(value=item) for item in embeddings_attr]
            return embeddings

        except Exception as e:
            raise RuntimeError(
                f"An error occurred during embedding generation: {str(e)}"
            )

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
