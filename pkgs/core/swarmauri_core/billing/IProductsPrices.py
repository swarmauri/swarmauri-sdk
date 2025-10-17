"""Product and price catalog interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .protos import PriceRefProto, PriceSpecProto, ProductRefProto, ProductSpecProto


class IProductsPrices(ABC):
    """Operations for managing products and prices."""

    @abstractmethod
    def create_product(
        self, product_spec: ProductSpecProto, *, idempotency_key: str
    ) -> ProductRefProto:
        """Create a product on the provider."""

    @abstractmethod
    def create_price(
        self,
        product: ProductRefProto,
        price_spec: PriceSpecProto,
        *,
        idempotency_key: str,
    ) -> PriceRefProto:
        """Create a price for the given product."""
