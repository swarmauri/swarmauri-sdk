"""Reusable component base for IDelegationService implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.delegation.IDelegationService import IDelegationService
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class DelegationServiceBase(IDelegationService, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(
        default=ResourceTypes.DELEGATION_SERVICE.value, frozen=True
    )
    type: Literal["DelegationServiceBase"] = "DelegationServiceBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
