from collections.abc import Sequence
from typing import Any, Dict, List, Literal, Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


def _vector_value(value: Any) -> List[float]:
    if hasattr(value, "value"):
        value = value.value
    if isinstance(value, Sequence) and value and hasattr(value[0], "value"):
        value = value[0].value
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError("image embedder must return a numeric vector")
    vector = [float(number) for number in value]
    if not vector:
        raise ValueError("embedding must not be empty")
    return vector


def _as_result(item: Any, rank: int) -> Dict[str, Any]:
    if isinstance(item, dict):
        result = dict(item)
    elif hasattr(item, "model_dump"):
        result = item.model_dump(mode="json")
    else:
        result = {
            "content": getattr(item, "content", str(item)),
            "metadata": getattr(item, "metadata", {}),
        }
        for name in ("id", "score", "uri"):
            value = getattr(item, name, None)
            if value is not None:
                result[name] = value
    result["rank"] = rank
    result.setdefault("metadata", {})
    return result


@ComponentBase.register_type(ToolBase, "QueryImageVectorStoreTool")
class QueryImageVectorStoreTool(ToolBase):
    version: str = "0.1.0.dev1"
    name: str = "QueryImageVectorStoreTool"
    description: str = "Query an image vector store with an image or embedding."
    type: Literal["QueryImageVectorStoreTool"] = "QueryImageVectorStoreTool"
    vector_store: Any = Field(default=None, exclude=True)
    image_embedder: Any = Field(default=None, exclude=True)
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="image",
                input_type="object",
                description="Image input accepted by the configured embedder.",
                required=False,
            ),
            Parameter(
                name="embedding",
                input_type="array",
                description="Precomputed image embedding.",
                required=False,
            ),
            Parameter(
                name="top_k",
                input_type="integer",
                description="Maximum number of ranked results.",
                required=False,
            ),
            Parameter(
                name="metadata_filter",
                input_type="object",
                description="Exact-match metadata constraints.",
                required=False,
            ),
        ]
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __call__(
        self,
        image: Any = None,
        embedding: Optional[Sequence[float]] = None,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if (image is None) == (embedding is None):
            raise ValueError("provide exactly one of image or embedding")
        if not 1 <= top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")
        if self.vector_store is None:
            raise ValueError("vector_store must be configured")

        if image is not None:
            infer = getattr(self.image_embedder, "infer_vector", None)
            if not callable(infer):
                raise ValueError("image_embedder must provide infer_vector(image)")
            embedding_value = _vector_value(infer(image))
        else:
            embedding_value = _vector_value(embedding)

        search = getattr(self.vector_store, "retrieve_by_vector", None)
        if not callable(search):
            search = getattr(self.vector_store, "similarity_search_by_vector", None)
        if not callable(search):
            raise ValueError(
                "vector_store must provide retrieve_by_vector or similarity_search_by_vector"
            )

        candidate_count = top_k if not metadata_filter else min(top_k * 5, 500)
        try:
            items = search(embedding_value, top_k=candidate_count)
        except Exception as exc:
            raise RuntimeError("image vector-store retrieval failed") from exc

        results: List[Dict[str, Any]] = []
        for item in items or []:
            normalized = _as_result(item, len(results) + 1)
            metadata = normalized.get("metadata")
            if metadata_filter and not (
                isinstance(metadata, dict)
                and all(metadata.get(k) == v for k, v in metadata_filter.items())
            ):
                continue
            normalized["rank"] = len(results) + 1
            results.append(normalized)
            if len(results) == top_k:
                break
        return results
