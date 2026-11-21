"""Reusable component base for IGrantStore implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.delegation.IGrantStore import IGrantStore
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class GrantStoreBase(IGrantStore, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(default=ResourceTypes.GRANT_STORE.value, frozen=True)
    type: Literal["GrantStoreBase"] = "GrantStoreBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
