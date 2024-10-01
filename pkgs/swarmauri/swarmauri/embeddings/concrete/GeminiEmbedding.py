import google.generativeai as genai
from typing import List, Literal, Any, Optional
from pydantic import PrivateAttr
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.embeddings.base.EmbeddingBase import EmbeddingBase


class GeminiEmbedding(EmbeddingBase):
    """
    A class for generating embeddings using the Google Gemini API.

    This class allows users to obtain embeddings for text data using specified models
    from the Gemini API.

    Attributes:
        model (str): The model to use for generating embeddings. Defaults to 'text-embedding-004'.
        task_type (str): The type of task for which the embeddings are generated. Defaults to 'unspecified'.
        output_dimensionality (int): The desired dimensionality of the output embeddings.
        api_key (str): API key for authenticating requests to the Gemini API.

    Raises:
        ValueError: If an invalid model or task type is provided during initialization.

    Example:
        >>> gemini_embedding = GeminiEmbedding(api_key='your_api_key', model='text-embedding-004')
        >>> embeddings = gemini_embedding.infer_vector(["Hello, world!", "Data science is awesome."])
    """

    type: Literal["GeminiEmbedding"] = "GeminiEmbedding"

    _allowed_models: List[str] = PrivateAttr(
        default=["text-embedding-004", "embedding-001"]
    )
    _allowed_task_types: List[str] = PrivateAttr(
        default=[
            "unspecified",
            "retrieval_query",
            "retrieval_document",
            "semantic_similarity",
            "classification",
            "clustering",
            "question_answering",
            "fact_verification",
        ]
    )

    model: str = "text-embedding-004"
    _task_type: str = PrivateAttr("unspecified")
    _output_dimensionality: int = PrivateAttr(None)
    api_key: str = None
    _client: Any = PrivateAttr()

    def __init__(
        self,
        api_key: str = None,
        model: str = "text-embedding-004",
        task_type: Optional[str] = "unspecified",
        output_dimensionality: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if model not in self._allowed_models:
            raise ValueError(
                f"Invalid model '{model}'. Allowed models are: {', '.join(self._allowed_models)}"
            )

        if task_type not in self._allowed_task_types:
            raise ValueError(
                f"Invalid task_type '{task_type}'. Allowed task types are: {', '.join(self._allowed_task_types)}"
            )

        self.model = model
        self._task_type = task_type
        self._output_dimensionality = output_dimensionality
        self._client = genai
        self._client.configure(api_key=api_key)

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

            response = self._client.embed_content(
                model=f"models/{self.model}",
                content=data,
                task_type=self._task_type,
                output_dimensionality=self._output_dimensionality,
            )

            embeddings = [Vector(value=item) for item in response["embedding"]]
            return embeddings

        except Exception as e:
            raise RuntimeError(
                f"An error occurred during embedding generation: {str(e)}"
            )

    def save_model(self, path: str):
        raise NotImplementedError("save_model is not applicable for Gemini embeddings")

    def load_model(self, path: str):
        raise NotImplementedError("load_model is not applicable for Gemini embeddings")

    def fit(self, documents: List[str], labels=None):
        raise NotImplementedError("fit is not applicable for Gemini embeddings")

    def transform(self, data: List[str]):
        raise NotImplementedError("transform is not applicable for Gemini embeddings")

    def fit_transform(self, documents: List[str], **kwargs):
        raise NotImplementedError(
            "fit_transform is not applicable for Gemini embeddings"
        )

    def extract_features(self):
        raise NotImplementedError(
            "extract_features is not applicable for Gemini embeddings"
        )
