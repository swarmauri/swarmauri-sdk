"""Paystack billing provider implementation."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from pydantic import Field, PrivateAttr, SecretStr

from swarmauri_base.billing import (
    BillingProviderBase,
    CheckoutIntentRef,
    CheckoutRequest,
    HostedCheckoutMixin,
    InvoicingMixin,
    InvoiceSpec,
    MarketplaceMixin,
    OnlinePaymentsMixin,
    PaymentIntentRequest,
    PaymentRef,
    PriceRef,
    PriceSpec,
    ProductRef,
    ProductSpec,
    ProductsPricesMixin,
    RiskMixin,
    SplitSpec,
    SubscriptionSpec,
    SubscriptionsMixin,
)


class PaystackBillingProvider(
    ProductsPricesMixin,
    HostedCheckoutMixin,
    OnlinePaymentsMixin,
    SubscriptionsMixin,
    InvoicingMixin,
    MarketplaceMixin,
    RiskMixin,
    BillingProviderBase,
):
    """Billing provider backed by the Paystack Python SDK."""

    component_name: str = "paystack"
    secret_key: SecretStr = Field(repr=False)
    _tx: Any = PrivateAttr(default=None)
    _product: Any = PrivateAttr(default=None)
    _sub: Any = PrivateAttr(default=None)
    _invoice: Any = PrivateAttr(default=None)
    _split: Any = PrivateAttr(default=None)

    def _ensure(self) -> None:
        if self._tx is None:
            from paystackapi.invoice import Invoice
            from paystackapi.paystack import Paystack
            from paystackapi.product import Product
            from paystackapi.split import Split
            from paystackapi.subscription import Subscription
            from paystackapi.transaction import Transaction

            Paystack.SECRET_KEY = self.secret_key.get_secret_value()
            self._tx, self._product, self._sub, self._invoice, self._split = (
                Transaction,
                Product,
                Subscription,
                Invoice,
                Split,
            )

    # ---------------------------------------------------------------- Products & Prices
    def _create_product(
        self, product_spec: ProductSpec, *, idempotency_key: str
    ) -> ProductRef:
        self._ensure()
        resp = self._product.create(
            name=product_spec.name,
            description=product_spec.description or "",
            price=0,
            currency="NGN",
        )
        if not resp.get("status"):
            raise RuntimeError(resp.get("message", "product create failed"))
        ref = ProductRef(
            id=str(resp["data"]["id"]),
            provider=self.component_name,
            raw=resp,
        )
        return ref

    def _create_price(
        self,
        product: ProductRef,
        price_spec: PriceSpec,
        *,
        idempotency_key: str,
    ) -> PriceRef:
        self._ensure()
        resp = self._product.create(
            name=f"{product.id}-sku",
            description=price_spec.nickname or "",
            price=price_spec.unit_amount_minor,
            currency=price_spec.currency.upper(),
        )
        if not resp.get("status"):
            raise RuntimeError(resp.get("message", "price create failed"))
        data = resp["data"]
        ref = PriceRef(
            id=data.get("product_code") or str(data.get("id")),
            product_id=product.id,
            currency=data.get("currency"),
            unit_amount_minor=data.get("price"),
            provider=self.component_name,
            raw=resp,
        )
        return ref

    # ---------------------------------------------------------------- Hosted Checkout
    def _create_checkout(
        self, price: PriceRef, request: CheckoutRequest
    ) -> CheckoutIntentRef:
        self._ensure()
        init = self._tx.initialize(
            reference=request.idempotency_key or f"chk-{price.id}",
            amount=price.raw["data"]["price"],
            currency=price.raw["data"]["currency"],
            email=request.customer_email or "buyer@example.com",
            metadata={"product_id": price.product_id, "price_code": price.id},
            callback_url=request.success_url,
        )
        if not init.get("status"):
            raise RuntimeError(init.get("message", "init failed"))
        intent = CheckoutIntentRef(
            id=init["data"]["reference"],
            url=init["data"]["authorization_url"],
            provider=self.component_name,
            raw=init,
        )
        return intent

    # ---------------------------------------------------------------- Online Payments
    def _create_payment_intent(self, req: PaymentIntentRequest) -> PaymentRef:
        self._ensure()
        init = self._tx.initialize(
            reference=req.idempotency_key or "ref",
            amount=req.amount_minor,
            currency=req.currency.upper(),
            email="buyer@example.com",
            metadata=req.metadata,
        )
        if not init.get("status"):
            raise RuntimeError(init.get("message", "init failed"))
        ref = PaymentRef(
            id=init["data"]["reference"],
            status="initialized",
            provider=self.component_name,
            raw=init,
        )
        return ref

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRef:
        ref = PaymentRef(
            id=payment_id,
            status="not_applicable",
            provider=self.component_name,
            raw=None,
        )
        return ref

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRef:
        ref = PaymentRef(
            id=payment_id,
            status="canceled_requested",
            provider=self.component_name,
            raw=None,
        )
        return ref

    # ---------------------------------------------------------------- Subscriptions
    def _create_subscription(
        self, spec: SubscriptionSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._ensure()
        authorization = spec.metadata.get("authorization")
        sub = self._sub.create(
            customer=spec.customer_id,
            plan=spec.items[0].price_id,
            authorization=authorization,
        )
        if not sub.get("status"):
            raise RuntimeError(sub.get("message", "subscription failed"))
        result = {
            "subscription_code": sub["data"]["subscription_code"],
            "status": sub["message"],
            "provider": self.component_name,
            "raw": sub,
        }
        return result

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        self._ensure()
        res = self._sub.disable(code=subscription_id, token=None)
        result = {
            "subscription_code": subscription_id,
            "status": res.get("message", "disabled"),
            "provider": self.component_name,
            "raw": res,
        }
        return result

    # ---------------------------------------------------------------- Invoicing
    def _create_invoice(
        self, spec: InvoiceSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._ensure()
        amount = sum((line.amount_minor or 0) for line in spec.line_items)
        inv = self._invoice.create(
            customer=spec.customer_id,
            amount=amount,
            currency="NGN",
            due_date=None,
            description="Invoice",
        )
        if not inv.get("status"):
            raise RuntimeError(inv.get("message", "invoice create failed"))
        result = {
            "invoice_id": inv["data"]["invoice_code"],
            "status": "created",
            "provider": self.component_name,
            "raw": inv,
        }
        return result

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        result = {
            "invoice_id": invoice_id,
            "status": "finalized",
            "provider": self.component_name,
            "raw": None,
        }
        return result

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        self._ensure()
        res = self._invoice.notify(invoice_code=invoice_id)
        result = {
            "invoice_id": invoice_id,
            "status": "void_requested",
            "provider": self.component_name,
            "raw": res,
        }
        return result

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        result = {
            "invoice_id": invoice_id,
            "status": "uncollectible",
            "provider": self.component_name,
            "raw": None,
        }
        return result

    # ---------------------------------------------------------------- Marketplace
    def _create_split(
        self, spec: SplitSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._ensure()
        entries = [{"subaccount": e.account, "share": e.share} for e in spec.entries]
        sp = self._split.create(
            name=spec.name,
            type=spec.type,
            currency=spec.currency.upper(),
            subaccounts=entries,
            bearer_type="account",
            bearer_subaccount=None,
        )
        if not sp.get("status"):
            raise RuntimeError(sp.get("message", "split create failed"))
        result = {
            "split_code": sp["data"]["split_code"],
            "provider": self.component_name,
            "raw": sp,
        }
        return result

    def _charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        self._ensure()
        init = self._tx.initialize(
            reference=idempotency_key,
            amount=amount_minor,
            currency=currency.upper(),
            email="buyer@example.com",
            split_code=split_code_or_params["split_code"],
        )
        if not init.get("status"):
            raise RuntimeError(init.get("message", "init failed"))
        result = {
            "reference": init["data"]["reference"],
            "authorization_url": init["data"]["authorization_url"],
            "provider": self.component_name,
            "raw": init,
        }
        return result

    # ---------------------------------------------------------------- Risk
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        import hashlib
        import hmac

        signature = headers.get("X-Paystack-Signature", "")
        digest = hmac.new(secret.encode(), raw_body, hashlib.sha512).hexdigest()
        result = hmac.compare_digest(digest, signature)
        return result

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        from paystackapi.dispute import Dispute

        res = Dispute.list()
        data = res.get("data", []) if isinstance(res, dict) else []
        return data


__all__ = ["PaystackBillingProvider"]
