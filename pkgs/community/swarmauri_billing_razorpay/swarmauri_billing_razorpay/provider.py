"""Razorpay billing provider implementation."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, cast

from pydantic import Field, PrivateAttr, SecretStr

from swarmauri_base.billing import (
    BillingProviderBase,
    BillingSpec,
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
    RefundRequest,
    RefundsMixin,
    RiskMixin,
    SplitSpec,
    SubscriptionSpec,
    SubscriptionsMixin,
)


class RazorpayBillingProvider(
    ProductsPricesMixin,
    HostedCheckoutMixin,
    OnlinePaymentsMixin,
    SubscriptionsMixin,
    InvoicingMixin,
    MarketplaceMixin,
    RefundsMixin,
    RiskMixin,
    BillingProviderBase,
):
    """Billing provider backed by the Razorpay Python SDK."""

    component_name: str = "razorpay"
    key_id: SecretStr = Field(repr=False)
    key_secret: SecretStr = Field(repr=False)
    _client: Any = PrivateAttr(default=None)

    # ------------------------------------------------------------------ Client
    def _rz(self) -> Any:
        if self._client is None:
            import razorpay

            self._client = razorpay.Client(
                auth=(
                    self.key_id.get_secret_value(),
                    self.key_secret.get_secret_value(),
                )
            )
        return self._client

    @staticmethod
    def _require(spec: BillingSpec | Any, field: str) -> Any:
        value = getattr(
            spec, "resolve", lambda name, default=None: getattr(spec, name, default)
        )(field)
        if value is None or (isinstance(value, str) and not value):
            raise ValueError(f"{field} is required for {spec.__class__.__name__}")
        return value

    # ---------------------------------------------------------------- Products & Prices
    def _create_product(
        self, product_spec: ProductSpec, *, idempotency_key: str
    ) -> ProductRef:
        client = self._rz()
        name = self._require(product_spec, "name")
        description = (
            product_spec.resolve("description") or product_spec.resolve("sku") or ""
        )
        item = client.item.create(
            {
                "name": name,
                "description": description,
                "amount": int(product_spec.resolve("amount") or 0),
                "currency": str(product_spec.resolve("currency") or "INR").upper(),
            }
        )
        ref = ProductRef(
            id=item["id"],
            provider=self.component_name,
            name=item.get("name"),
            description=item.get("description"),
            raw=item,
        )
        return ref

    def _create_price(
        self,
        product: ProductRef,
        price_spec: PriceSpec,
        *,
        idempotency_key: str,
    ) -> PriceRef:
        client = self._rz()
        amount = int(self._require(price_spec, "unit_amount_minor"))
        currency = str(self._require(price_spec, "currency")).upper()
        nickname = price_spec.resolve("nickname") or f"{product.id}-price"
        priced = client.item.create(
            {
                "name": nickname,
                "amount": amount,
                "currency": currency,
                "description": nickname,
            }
        )
        ref = PriceRef(
            id=priced["id"],
            product_id=product.id,
            currency=priced.get("currency"),
            unit_amount_minor=priced.get("amount"),
            provider=self.component_name,
            raw=priced,
        )
        return ref

    # ---------------------------------------------------------------- Hosted Checkout
    def _create_checkout(
        self, price: PriceRef, request: CheckoutRequest
    ) -> CheckoutIntentRef:
        client = self._rz()
        body = {
            "amount": price.unit_amount_minor or price.raw.get("amount", 0),
            "currency": price.currency or price.raw.get("currency", "INR"),
            "description": f"Purchase {price.product_id}",
            "reference_id": request.resolve("idempotency_key") or f"chk-{price.id}",
            "notify": {"email": True},
            "callback_url": self._require(request, "success_url"),
            "callback_method": "get",
        }
        if request.resolve("customer_email"):
            body["customer"] = {"email": request.resolve("customer_email")}
        link = client.payment_link.create(body)
        intent = CheckoutIntentRef(
            id=link["id"],
            url=link.get("short_url"),
            provider=self.component_name,
            raw=link,
        )
        return intent

    # ---------------------------------------------------------------- Online Payments
    def _create_payment_intent(self, req: PaymentIntentRequest) -> PaymentRef:
        client = self._rz()
        amount = int(self._require(req, "amount_minor"))
        currency = str(self._require(req, "currency")).upper()
        order = client.order.create(
            {
                "amount": amount,
                "currency": currency,
                "receipt": req.resolve("idempotency_key") or "receipt",
            }
        )
        ref = PaymentRef(
            id=order["id"],
            status=order.get("status"),
            amount_minor=order.get("amount"),
            currency=order.get("currency"),
            provider=self.component_name,
            raw=order,
        )
        return ref

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRef:
        client = self._rz()
        existing = client.payment.fetch(payment_id)
        amount = existing.get("amount")
        if amount is None:
            raise RuntimeError("Razorpay payment capture requires a payment amount")
        payment = client.payment.capture(
            payment_id,
            amount,
            data={"currency": existing.get("currency", "INR")},
        )
        ref = PaymentRef(
            id=payment["id"],
            status=payment.get("status"),
            amount_minor=payment.get("amount"),
            currency=payment.get("currency"),
            provider=self.component_name,
            raw=payment,
        )
        return ref

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRef:
        client = self._rz()
        payment = client.payment.refund(
            payment_id,
            data={
                "speed": "optimum",
                "notes": {"reason": reason} if reason else {},
            },
        )
        ref = PaymentRef(
            id=payment["id"],
            status=payment.get("status", "refunded"),
            amount_minor=payment.get("amount"),
            currency=payment.get("currency"),
            provider=self.component_name,
            raw=payment,
        )
        return ref

    # ---------------------------------------------------------------- Subscriptions
    def _create_subscription(
        self, spec: SubscriptionSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        if not spec.items:
            raise ValueError("SubscriptionSpec.items must contain at least one entry")
        client = self._rz()
        plan_id = self._require(spec.items[0], "price_id")
        subscription = client.subscription.create(
            {
                "plan_id": plan_id,
                "total_count": 999999,
                "customer_notify": 1,
            }
        )
        result = {
            "subscription_id": subscription["id"],
            "status": subscription.get("status"),
            "provider": self.component_name,
            "raw": subscription,
        }
        return result

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        client = self._rz()
        subscription = client.subscription.cancel(
            subscription_id,
            data={"cancel_at_cycle_end": at_period_end},
        )
        result = {
            "subscription_id": subscription["id"],
            "status": subscription.get("status"),
            "provider": self.component_name,
            "raw": subscription,
        }
        return result

    # ---------------------------------------------------------------- Invoicing
    def _create_invoice(
        self, spec: InvoiceSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        client = self._rz()
        customer_ref = self._require(spec, "customer_id")
        if str(customer_ref).startswith("cust_"):
            customer_payload: Mapping[str, Any] = {"id": customer_ref}
        else:
            customer_payload = {"email": customer_ref}
        invoice = client.invoice.create(
            {
                "type": "invoice",
                "customer": customer_payload,
                "line_items": [
                    {
                        "name": item.description or "Item",
                        "amount": item.amount_minor or 0,
                        "currency": item.currency or "INR",
                        "quantity": item.quantity,
                    }
                    for item in spec.line_items
                ],
            }
        )
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status"),
            "provider": self.component_name,
            "raw": invoice,
        }
        return result

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        client = self._rz()
        invoice = client.invoice.issue(invoice_id)
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status"),
            "provider": self.component_name,
            "raw": invoice,
        }
        return result

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        client = self._rz()
        invoice = client.invoice.cancel(invoice_id)
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status", "cancelled"),
            "provider": self.component_name,
            "raw": invoice,
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
        result = {
            "split": spec.model_dump(mode="json"),
            "provider": self.component_name,
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
        client = self._rz()
        payment_id = split_code_or_params["payment_id"]
        transfers = client.payment.transfer(
            payment_id, data={"transfers": split_code_or_params["transfers"]}
        )
        result = {
            "payment_id": payment_id,
            "transfers": transfers,
            "provider": self.component_name,
            "raw": transfers,
        }
        return result

    # ---------------------------------------------------------------- Refunds
    def _create_refund(
        self, payment: PaymentRef, req: RefundRequest, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        client = self._rz()
        data: dict[str, Any] = {
            "speed": str(req.resolve("speed", "optimum")),
        }
        if req.amount_minor is not None:
            data["amount"] = req.amount_minor
        notes = dict(req.metadata or {})
        if req.reason:
            notes.setdefault("reason", req.reason)
        if notes:
            data["notes"] = notes
        refund = client.payment.refund(payment.id, data=data)
        return {
            "id": refund["id"],
            "status": refund.get("status"),
            "provider": self.component_name,
            "raw": refund,
        }

    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        client = self._rz()
        refund = client.refund.fetch(refund_id)
        return {
            "id": refund["id"],
            "status": refund.get("status"),
            "provider": self.component_name,
            "raw": refund,
        }

    # ---------------------------------------------------------------- Risk
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        import hashlib
        import hmac

        signature = headers.get("X-Razorpay-Signature", "")
        digest = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
        result = hmac.compare_digest(digest, signature)
        return result

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        client = self._rz()
        disputes = client.dispute.all({"count": limit})
        if isinstance(disputes, Mapping):
            data = cast(Sequence[Mapping[str, Any]], disputes.get("items", []))
        else:
            data = tuple()
        return data


__all__ = ["RazorpayBillingProvider"]
