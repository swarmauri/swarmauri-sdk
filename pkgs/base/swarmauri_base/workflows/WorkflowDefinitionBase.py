"""Reusable component base for IWorkflowDefinition implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.workflows.IWorkflowDefinition import IWorkflowDefinition
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class WorkflowDefinitionBase(IWorkflowDefinition, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(
        default=ResourceTypes.WORKFLOW_DEFINITION.value, frozen=True
    )
    type: Literal["WorkflowDefinitionBase"] = "WorkflowDefinitionBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
