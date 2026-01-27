"""Hosted checkout interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .protos import CheckoutIntentProto, CheckoutReqProto, PriceRefProto


class IHostedCheckout(ABC):
    """Operations for hosted checkout flows."""

    @abstractmethod
    def create_checkout(
        self, price: PriceRefProto, request: CheckoutReqProto
    ) -> CheckoutIntentProto:
        """Create a hosted checkout intent for the supplied price."""
