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
        self._pre(
            "create_product",
            provider=self.component_name,
            spec=product_spec.model_dump(mode="json"),
            idempotency_key=idempotency_key,
        )
        client = self._rz()
        name = self._require(product_spec, "name")
        description = (
            product_spec.resolve("description") or product_spec.resolve("sku") or ""
        )
        item = client.item.create(
            {
                "name": name,
                "description": description,
                "amount": 0,
                "currency": "INR",
            }
        )
        ref = ProductRef(
            id=item["id"],
            provider=self.component_name,
            name=item.get("name"),
            description=item.get("description"),
            raw=item,
        )
        self._post("create_product", ref)
        return ref

    def _create_price(
        self,
        product: ProductRef,
        price_spec: PriceSpec,
        *,
        idempotency_key: str,
    ) -> PriceRef:
        self._pre(
            "create_price",
            provider=self.component_name,
            product_id=product.id,
            spec=price_spec.model_dump(mode="json"),
            idempotency_key=idempotency_key,
        )
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
        self._post("create_price", ref)
        return ref

    # ---------------------------------------------------------------- Hosted Checkout
    def _create_checkout(
        self, price: PriceRef, request: CheckoutRequest
    ) -> CheckoutIntentRef:
        self._pre(
            "create_checkout",
            provider=self.component_name,
            price_id=price.id,
            request=request.model_dump(mode="json"),
        )
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
        self._post("create_checkout", intent)
        return intent

    # ---------------------------------------------------------------- Online Payments
    def _create_payment_intent(self, req: PaymentIntentRequest) -> PaymentRef:
        self._pre(
            "create_payment_intent",
            provider=self.component_name,
            request=req.model_dump(mode="json"),
        )
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
        self._post("create_payment_intent", ref)
        return ref

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRef:
        self._pre(
            "capture_payment",
            provider=self.component_name,
            payment_id=payment_id,
            idempotency_key=idempotency_key,
        )
        client = self._rz()
        payment = client.payment.capture(payment_id, data={"amount": None})
        ref = PaymentRef(
            id=payment["id"],
            status=payment.get("status"),
            provider=self.component_name,
            raw=payment,
        )
        self._post("capture_payment", ref)
        return ref

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRef:
        self._pre(
            "cancel_payment",
            provider=self.component_name,
            payment_id=payment_id,
            reason=reason,
            idempotency_key=idempotency_key,
        )
        client = self._rz()
        payment = client.payment.refund(payment_id, data={"speed": "optimum"})
        ref = PaymentRef(
            id=payment["id"],
            status=payment.get("status", "refunded"),
            provider=self.component_name,
            raw=payment,
        )
        self._post("cancel_payment", ref)
        return ref

    # ---------------------------------------------------------------- Subscriptions
    def _create_subscription(
        self, spec: SubscriptionSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre(
            "create_subscription",
            provider=self.component_name,
            spec=spec.model_dump(mode="json"),
            idempotency_key=idempotency_key,
        )
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
        self._post("create_subscription", result)
        return result

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        self._pre(
            "cancel_subscription",
            provider=self.component_name,
            subscription_id=subscription_id,
            at_period_end=at_period_end,
        )
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
        self._post("cancel_subscription", result)
        return result

    # ---------------------------------------------------------------- Invoicing
    def _create_invoice(
        self, spec: InvoiceSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre(
            "create_invoice",
            provider=self.component_name,
            spec=spec.model_dump(mode="json"),
            idempotency_key=idempotency_key,
        )
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
        self._post("create_invoice", result)
        return result

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        self._pre(
            "finalize_invoice",
            provider=self.component_name,
            invoice_id=invoice_id,
        )
        client = self._rz()
        invoice = client.invoice.issue(invoice_id)
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status"),
            "provider": self.component_name,
            "raw": invoice,
        }
        self._post("finalize_invoice", result)
        return result

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        self._pre(
            "void_invoice",
            provider=self.component_name,
            invoice_id=invoice_id,
        )
        client = self._rz()
        invoice = client.invoice.cancel(invoice_id)
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status", "cancelled"),
            "provider": self.component_name,
            "raw": invoice,
        }
        self._post("void_invoice", result)
        return result

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        self._pre(
            "mark_uncollectible",
            provider=self.component_name,
            invoice_id=invoice_id,
        )
        result = {
            "invoice_id": invoice_id,
            "status": "uncollectible",
            "provider": self.component_name,
            "raw": None,
        }
        self._post("mark_uncollectible", result)
        return result

    # ---------------------------------------------------------------- Marketplace
    def _create_split(
        self, spec: SplitSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre(
            "create_split",
            provider=self.component_name,
            spec=spec.model_dump(mode="json"),
            idempotency_key=idempotency_key,
        )
        result = {
            "split": spec.model_dump(mode="json"),
            "provider": self.component_name,
        }
        self._post("create_split", result)
        return result

    def _charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        self._pre(
            "charge_with_split",
            provider=self.component_name,
            amount_minor=amount_minor,
            currency=currency,
            split=split_code_or_params,
            idempotency_key=idempotency_key,
        )
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
        self._post("charge_with_split", result)
        return result

    # ---------------------------------------------------------------- Risk
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        self._pre(
            "verify_webhook_signature",
            provider=self.component_name,
            has_headers=bool(headers),
        )
        import hashlib
        import hmac

        signature = headers.get("X-Razorpay-Signature", "")
        digest = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
        result = hmac.compare_digest(digest, signature)
        self._post("verify_webhook_signature", result)
        return result

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        self._pre(
            "list_disputes",
            provider=self.component_name,
            limit=limit,
        )
        client = self._rz()
        settlements = client.payments.fetch_settlements()
        if isinstance(settlements, Mapping):
            data = cast(Sequence[Mapping[str, Any]], settlements.get("items", []))
        else:
            data = tuple()
        self._post("list_disputes", data)
        return data


__all__ = ["RazorpayBillingProvider"]
