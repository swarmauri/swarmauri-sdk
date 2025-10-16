"""Mixin implementing the product and price catalog interface."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping, cast

from swarmauri_core.billing import IProductsPrices
from swarmauri_core.billing.protos import (
    PriceRefProto,
    PriceSpecProto,
    ProductRefProto,
    ProductSpecProto,
)

from .OperationDispatcherMixin import OperationDispatcherMixin, extract_raw_payload
from .refs import PriceRef, ProductRef


class ProductsPricesMixin(OperationDispatcherMixin, IProductsPrices):
    """Common helpers for product and price lifecycle operations."""

    def create_product(
        self, product_spec: ProductSpecProto, *, idempotency_key: str
    ) -> ProductRefProto:
        self._require_idempotency(idempotency_key)
        result = self._create_product(product_spec, idempotency_key=idempotency_key)
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
        result = self._create_price(
            product, price_spec, idempotency_key=idempotency_key
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

    @abstractmethod
    def _create_product(
        self, product_spec: ProductSpecProto, *, idempotency_key: str
    ) -> ProductRefProto | Mapping[str, Any]:
        """Return a provider-specific representation for the created product."""

    @abstractmethod
    def _create_price(
        self,
        product: ProductRefProto,
        price_spec: PriceSpecProto,
        *,
        idempotency_key: str,
    ) -> PriceRefProto | Mapping[str, Any]:
        """Return a provider-specific representation for the created price."""


__all__ = ["ProductsPricesMixin"]
