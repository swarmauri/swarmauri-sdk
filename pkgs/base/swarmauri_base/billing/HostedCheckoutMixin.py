"""Mixin implementing hosted checkout support."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping, cast

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import IHostedCheckout
from swarmauri_core.billing.protos import (
    CheckoutIntentProto,
    CheckoutReqProto,
    PriceRefProto,
)

from .utils import extract_raw_payload
from .refs import CheckoutIntentRef


class HostedCheckoutMixin(BaseModel, IHostedCheckout):
    """Implements ``IHostedCheckout`` via provider-specific hooks."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def create_checkout(
        self, price: PriceRefProto, request: CheckoutReqProto
    ) -> CheckoutIntentProto:
        result = self._create_checkout(price, request)
        if isinstance(result, CheckoutIntentProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return CheckoutIntentRef(
            id=str(raw.get("id", getattr(payload, "get", lambda *_: "")("id", ""))),
            provider=str(raw.get("provider", "")),
            url=str(
                raw.get("url")
                or getattr(payload, "get", lambda *_: "")("url", "")
                or getattr(price, "url", "")
            ),
            raw=payload,
        )

    @abstractmethod
    def _create_checkout(
        self, price: PriceRefProto, request: CheckoutReqProto
    ) -> CheckoutIntentProto | Mapping[str, Any]:
        """Create a provider-specific checkout session."""


__all__ = ["HostedCheckoutMixin"]
