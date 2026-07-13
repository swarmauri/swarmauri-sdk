from typing import Any, Dict, List, Literal, Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "QueryImageVectorStoreTool")
class QueryImageVectorStoreTool(ToolBase):
    version: str = "1.0.0"
    name: str = "QueryImageVectorStoreTool"
    description: str = (
        "Query an image vector store by embedding or image and return ranked similar results."
    )
    type: Literal["QueryImageVectorStoreTool"] = "QueryImageVectorStoreTool"
    vector_store: Any = Field(default=None, exclude=True)
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="query",
                input_type="string",
                description="Embedding or image used to query the image vector store",
                required=True,
            ),
            Parameter(
                name="top_k",
                input_type="integer",
                description="Number of top similar results to return",
                required=False,
            ),
            Parameter(
                name="metadata_filter",
                input_type="object",
                description="Optional metadata filters applied to the search",
                required=False,
            ),
        ]
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __call__(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if self.vector_store is None:
            raise ValueError("vector_store must be set before calling this tool")

        kwargs: Dict[str, Any] = {"top_k": int(top_k)}
        if metadata_filter is not None:
            kwargs["metadata_filter"] = metadata_filter

        if hasattr(self.vector_store, "similarity_search"):
            results = self.vector_store.similarity_search(query, **kwargs)
        elif hasattr(self.vector_store, "retrieve"):
            results = self.vector_store.retrieve(query, **kwargs)
        else:
            raise AttributeError(
                "vector_store must implement retrieve or similarity_search"
            )

        ranked: List[Dict[str, Any]] = []
        for i, item in enumerate(results):
            if isinstance(item, dict):
                entry = {**item, "rank": i + 1}
            else:
                entry = {
                    "rank": i + 1,
                    "content": getattr(item, "content", str(item)),
                    "metadata": getattr(item, "metadata", {}),
                    "score": getattr(item, "score", None),
                }
            ranked.append(entry)
        return ranked
