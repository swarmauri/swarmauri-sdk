from typing import Any, Dict, List, Literal, Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


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
        for name in ("id", "score"):
            value = getattr(item, name, None)
            if value is not None:
                result[name] = value
    result["rank"] = rank
    result.setdefault("metadata", {})
    return result


def _matches(metadata: Any, expected: Dict[str, Any]) -> bool:
    return isinstance(metadata, dict) and all(
        metadata.get(key) == value for key, value in expected.items()
    )


@ComponentBase.register_type(ToolBase, "QueryKnowledgeBaseTool")
class QueryKnowledgeBaseTool(ToolBase):
    version: str = "0.1.0.dev1"
    name: str = "QueryKnowledgeBaseTool"
    description: str = "Retrieve ranked, structured knowledge-base results."
    type: Literal["QueryKnowledgeBaseTool"] = "QueryKnowledgeBaseTool"
    knowledge_base: Any = Field(default=None, exclude=True)
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="query",
                input_type="string",
                description="Natural-language retrieval query.",
                required=True,
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
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if self.knowledge_base is None or not callable(
            getattr(self.knowledge_base, "retrieve", None)
        ):
            raise ValueError("knowledge_base must provide retrieve(query, top_k)")
        if not query.strip():
            raise ValueError("query must not be blank")
        if not 1 <= top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")

        candidate_count = top_k if not metadata_filter else min(top_k * 5, 500)
        try:
            items = self.knowledge_base.retrieve(query, top_k=candidate_count)
        except Exception as exc:
            raise RuntimeError("knowledge-base retrieval failed") from exc

        results: List[Dict[str, Any]] = []
        for item in items or []:
            normalized = _as_result(item, len(results) + 1)
            if metadata_filter and not _matches(
                normalized.get("metadata"), metadata_filter
            ):
                continue
            normalized["rank"] = len(results) + 1
            results.append(normalized)
            if len(results) == top_k:
                break
        return results
