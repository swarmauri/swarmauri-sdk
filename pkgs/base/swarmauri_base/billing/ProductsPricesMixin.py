"""Mixin implementing the product and price catalog interface."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import IProductsPrices, Operation
from swarmauri_core.billing.protos import (
    PriceRefProto,
    PriceSpecProto,
    ProductRefProto,
    ProductSpecProto,
)

from .OperationDispatcherMixin import OperationDispatcherMixin, extract_raw_payload
from .refs import PriceRef, ProductRef


class ProductsPricesMixin(OperationDispatcherMixin, IProductsPrices):
    """Implements ``IProductsPrices`` by delegating to ``_op``."""

    def create_product(
        self, product_spec: ProductSpecProto, *, idempotency_key: str
    ) -> ProductRefProto:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_PRODUCT,
            {"product_spec": product_spec},
            idempotency_key=idempotency_key,
        )
        if isinstance(result, ProductRefProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return ProductRef(
            id=str(raw.get("id", "")),
            provider=str(raw.get("provider", "")),
            raw=payload,
        )

    def create_price(
        self,
        product: ProductRefProto,
        price_spec: PriceSpecProto,
        *,
        idempotency_key: str,
    ) -> PriceRefProto:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_PRICE,
            {"product": product, "price_spec": price_spec},
            idempotency_key=idempotency_key,
        )
        if isinstance(result, PriceRefProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return PriceRef(
            id=str(raw.get("id", "")),
            product_id=str(raw.get("product_id", getattr(product, "id", ""))),
            provider=str(raw.get("provider", "")),
            raw=payload,
        )


__all__ = ["ProductsPricesMixin"]
