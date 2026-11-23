"""Reusable component base for IAuthorityStrategy implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.invocations.IAuthorityStrategy import IAuthorityStrategy
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class AuthorityStrategyBase(IAuthorityStrategy, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(
        default=ResourceTypes.AUTHORITY_STRATEGY.value, frozen=True
    )
    type: Literal["AuthorityStrategyBase"] = "AuthorityStrategyBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
