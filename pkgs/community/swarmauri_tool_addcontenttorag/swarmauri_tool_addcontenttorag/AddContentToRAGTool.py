from typing import Any, Dict, List, Literal, Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "AddContentToRAGTool")
class AddContentToRAGTool(ToolBase):
    """Add text content to a RAG knowledge base."""

    version: str = "0.1.0.dev1"
    name: str = "AddContentToRAGTool"
    description: str = (
        "Adds text content, with optional metadata tags, to a RAG "
        "knowledge base."
    )
    type: Literal["AddContentToRAGTool"] = "AddContentToRAGTool"
    knowledge_base: Any = Field(default=None, exclude=True)
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="content",
                input_type="string",
                description="Text to add to the knowledge base.",
                required=True,
            ),
            Parameter(
                name="metadata",
                input_type="object",
                description="Tags stored alongside the content.",
                required=False,
            ),
        ]
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __call__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add ``content`` to the configured knowledge base.

        Parameters:
            content (str): Text to add. Must not be blank or whitespace only.
            metadata (dict): Optional tags stored with the content. Defaults
                to an empty mapping.

        Returns:
            Dict[str, Any]: ``{"added": 1, "content_length": int,
            "metadata": dict}`` describing what was written.

        Raises:
            ValueError: the tool has no usable knowledge base, or ``content``
                is blank.
            RuntimeError: the knowledge base rejected the write. The original
                exception is chained and not exposed, so connection details
                stay out of the caller's view.

        The knowledge base is expected to provide
        ``add_documents(documents)``, the storage counterpart of the
        ``retrieve(query, top_k)`` interface used by
        ``QueryKnowledgeBaseTool``.
        """
        if self.knowledge_base is None or not callable(
            getattr(self.knowledge_base, "add_documents", None)
        ):
            raise ValueError(
                "knowledge_base must provide add_documents(documents)"
            )
        if not content.strip():
            raise ValueError("content must not be blank")

        document = {
            "content": content,
            "metadata": dict(metadata or {}),
        }

        try:
            self.knowledge_base.add_documents([document])
        except Exception as exc:
            raise RuntimeError("knowledge-base update failed") from exc

        return {
            "added": 1,
            "content_length": len(content),
            "metadata": document["metadata"],
        }
