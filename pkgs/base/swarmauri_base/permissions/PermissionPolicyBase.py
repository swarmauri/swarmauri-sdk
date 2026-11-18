"""Reusable component base for IPermissionPolicy implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.permissions.IPermissionPolicy import IPermissionPolicy
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class PermissionPolicyBase(IPermissionPolicy, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(
        default=ResourceTypes.PERMISSION_POLICY.value, frozen=True
    )
    type: Literal["PermissionPolicyBase"] = "PermissionPolicyBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
