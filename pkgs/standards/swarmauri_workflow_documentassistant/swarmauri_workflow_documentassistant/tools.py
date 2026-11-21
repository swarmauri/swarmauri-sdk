"""Model-visible arguments exclude task authority and credentials."""

from collections.abc import Callable
from typing import Literal
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.tools.ParameterBase import ParameterBase


@ComponentBase.register_type(ToolBase, "AuthorizedDocumentTool")
class AuthorizedDocumentTool(ToolBase):
    """Read one resource through a host-bound invocation function."""

    type: Literal["AuthorizedDocumentTool"] = "AuthorizedDocumentTool"
    name: str = "ReadDocument"
    description: str = "Read a document permitted for the current task."
    callback: Callable = Field(exclude=True, repr=False)
    parameters: list[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="resource",
                input_type="string",
                description="Exact document resource identifier",
                required=True,
            )
        ]
    )

    def __call__(self, resource: str):
        return self.callback(resource)
