from typing import Any, Dict, List, Literal, Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "QueryKnowledgeBaseTool")
class QueryKnowledgeBaseTool(ToolBase):
    version: str = "0.1.0"
    name: str = "QueryKnowledgeBaseTool"
    description: str = (
        "A tool that queries a knowledge base for relevant information based on a user query."
    )
    type: Literal["QueryKnowledgeBaseTool"] = "QueryKnowledgeBaseTool"
    knowledge_base: Optional[Any] = Field(
        default=None, exclude=True, description="The knowledge base to query"
    )

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="query",
                input_type="string",
                description="The query string to search against the knowledge base",
                required=True,
            )
        ]
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __call__(self, query: str) -> Dict[str, str]:
        if self.knowledge_base is None:
            raise ValueError("No knowledge base has been set for this tool.")

        results = self.knowledge_base.retrieve(query=query)
        if not results:
            return {"result": "No results found."}

        if isinstance(results, list):
            content = "\n".join(
                [r.content if hasattr(r, "content") else str(r) for r in results]
            )
            return {"result": content}

        return {"result": str(results)}
