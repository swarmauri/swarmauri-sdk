"""Base provider implementation shared by all billing providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, FrozenSet, Mapping, Optional, Tuple, Type

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.billing import (
    ALL_API_STRATEGIES,
    ALL_CAPABILITIES,
    Capability,
    IBillingProvider,
    Operation,
)


class BillingProviderBase(
    ComponentBase,
    IBillingProvider,
    ABC,
):
    """Base class for billing providers that delegates to mixin dispatch."""

    CAPABILITIES: ClassVar[FrozenSet[Capability]] = ALL_CAPABILITIES

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    api_key: str = Field(
        ..., description="API key used to authenticate with the billing provider"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Optional base URL override for the provider API.",
    )
    timeout: float = Field(
        default=30.0,
        description="Timeout in seconds for provider requests.",
    )

    resource: str = Field(default="BillingProvider")

    @abstractmethod
    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        """Concrete providers must implement the dispatch method."""

    def _op(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> Any:
        self._pre(operation.value, payload=payload, idempotency_key=idempotency_key)
        result = self._dispatch(operation, payload, idempotency_key=idempotency_key)
        self._post(operation.value, result)
        return result

    # Hooks -----------------------------------------------------------------
    def _pre(self, action: str, **metadata: Any) -> None:
        """Hook executed before delegating to ``_dispatch``."""

        logger = getattr(self, "logger", None)
        if logger is not None:
            logger.debug("billing.%s.pre", action, extra={"payload": metadata})

    def _post(self, action: str, response: Any) -> None:
        """Hook executed after ``_dispatch`` returns."""

        logger = getattr(self, "logger", None)
        if logger is not None:
            logger.debug("billing.%s.post", action, extra={"response": response})

    @property
    def capabilities(self) -> FrozenSet[Capability]:
        return self.CAPABILITIES

    @property
    def api_strategies(self) -> Tuple[Type[Any], ...]:
        return ALL_API_STRATEGIES
