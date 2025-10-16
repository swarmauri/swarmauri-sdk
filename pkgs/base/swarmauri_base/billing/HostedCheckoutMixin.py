"""Mixin implementing hosted checkout support."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import IHostedCheckout, Operation
from swarmauri_core.billing.protos import (
    CheckoutIntentProto,
    CheckoutReqProto,
    PriceRefProto,
)

from .OperationDispatcherMixin import OperationDispatcherMixin, extract_raw_payload
from .refs import CheckoutIntentRef


class HostedCheckoutMixin(OperationDispatcherMixin, IHostedCheckout):
    """Implements ``IHostedCheckout`` via ``_op`` delegation."""

    def create_checkout(
        self, price: PriceRefProto, request: CheckoutReqProto
    ) -> CheckoutIntentProto:
        result = self._op(
            Operation.CREATE_CHECKOUT,
            {"price": price, "request": request},
        )
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


__all__ = ["HostedCheckoutMixin"]
