"""Base provider implementation shared by all billing providers."""

from __future__ import annotations

from typing import Any, ClassVar, FrozenSet, Tuple, Type

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.billing import (
    ALL_API_STRATEGIES,
    ALL_CAPABILITIES,
    Capability,
    IBillingProvider,
)


class BillingProviderBase(ComponentBase, IBillingProvider):
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

    resource: str = Field(default="BillingProvider")

    def _pre(self, action: str, **metadata: Any) -> None:
        """Hook executed before delegating to the provider implementation."""

        logger = getattr(self, "logger", None)
        if logger is not None:
            logger.debug("billing.%s.pre", action, extra={"payload": metadata})

    def _post(self, action: str, response: Any) -> None:
        """Hook executed after the provider implementation returns."""

        logger = getattr(self, "logger", None)
        if logger is not None:
            logger.debug("billing.%s.post", action, extra={"response": response})

    @property
    def capabilities(self) -> FrozenSet[Capability]:
        return self.CAPABILITIES

    @property
    def api_strategies(self) -> Tuple[Type[Any], ...]:
        return ALL_API_STRATEGIES
