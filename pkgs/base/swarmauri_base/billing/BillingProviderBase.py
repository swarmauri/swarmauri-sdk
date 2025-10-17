"""Base provider implementation shared by all billing providers."""

from __future__ import annotations

from typing import ClassVar, FrozenSet

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.billing import ALL_CAPABILITIES, Capability, IBillingProvider


class BillingProviderBase(IBillingProvider, ComponentBase):
    """Base class for billing providers shared across concrete implementations."""

    CAPABILITIES: ClassVar[FrozenSet[Capability]] = ALL_CAPABILITIES

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    api_key: str = Field(
        ..., description="API key used to authenticate with the billing provider"
    )
    base_url: str | None = Field(
        default=None,
        description="Optional base URL override for the provider API.",
    )
    timeout: float = Field(
        default=30.0,
        description="Timeout in seconds for provider requests.",
    )

    resource: str = Field(default=ResourceTypes.BILLING_PROVIDER.value)

    @property
    def capabilities(self) -> FrozenSet[Capability]:
        return self.CAPABILITIES
