"""Production-ready Stripe billing provider implementation."""

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


class StripeBillingProvider(
    ProductsPricesMixin,
    HostedCheckoutMixin,
    OnlinePaymentsMixin,
    SubscriptionsMixin,
    InvoicingMixin,
    MarketplaceMixin,
    RiskMixin,
    BillingProviderBase,
):
    """Stripe billing provider backed by the official Stripe SDK."""

    component_name: str = "stripe"
    api_key: SecretStr = Field(repr=False)
    _stripe: Any = PrivateAttr(default=None)

    # ------------------------------------------------------------------ Utils
    def _client(self) -> Any:
        if self._stripe is None:
            import stripe

            stripe.api_key = self.api_key.get_secret_value()
            self._stripe = stripe
        return self._stripe

    @staticmethod
    def _require(spec: BillingSpec, field: str) -> Any:
        value = spec.resolve(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"{field} is required for {spec.__class__.__name__}")
        return value

    # ---------------------------------------------------------------- Products & Prices
    def _create_product(
        self, product_spec: ProductSpec, *, idempotency_key: str
    ) -> ProductRef:
        stripe = self._client()
        name = self._require(product_spec, "name")
        product = stripe.Product.create(
            name=name,
            description=product_spec.resolve("description") or None,
            metadata=product_spec.resolve("metadata") or None,
            idempotency_key=idempotency_key,
        )
        ref = ProductRef(
            id=product["id"],
            provider=self.component_name,
            name=product.get("name"),
            description=product.get("description"),
            metadata=product.get("metadata"),
            raw=product,
        )
        return ref

    def _create_price(
        self,
        product: ProductRef,
        price_spec: PriceSpec,
        *,
        idempotency_key: str,
    ) -> PriceRef:
        stripe = self._client()
        currency = self._require(price_spec, "currency")
        amount = int(self._require(price_spec, "unit_amount_minor"))
        price = stripe.Price.create(
            product=product.id,
            currency=str(currency).lower(),
            unit_amount=amount,
            nickname=price_spec.resolve("nickname"),
            metadata=price_spec.resolve("metadata") or None,
            idempotency_key=idempotency_key,
        )
        ref = PriceRef(
            id=price["id"],
            product_id=price.get("product"),
            currency=price.get("currency"),
            unit_amount_minor=price.get("unit_amount"),
            provider=self.component_name,
            raw=price,
        )
        return ref

    # ---------------------------------------------------------------- Hosted Checkout
    def _create_checkout(
        self, price: PriceRef, request: CheckoutRequest
    ) -> CheckoutIntentRef:
        stripe = self._client()
        success_url = self._require(request, "success_url")
        cancel_url = request.resolve("cancel_url") or success_url
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price.id, "quantity": request.quantity}],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=request.resolve("customer_email"),
            metadata=request.resolve("metadata") or None,
            idempotency_key=request.resolve("idempotency_key"),
        )
        intent = CheckoutIntentRef(
            id=session["id"],
            url=session.get("url"),
            provider=self.component_name,
            raw=session,
        )
        return intent

    # ---------------------------------------------------------------- Online Payments
    def _create_payment_intent(self, req: PaymentIntentRequest) -> PaymentRef:
        stripe = self._client()
        amount = int(self._require(req, "amount_minor"))
        currency = self._require(req, "currency")
        pi = stripe.PaymentIntent.create(
            amount=amount,
            currency=str(currency).lower(),
            payment_method=req.resolve("payment_method_id"),
            confirm=req.confirm,
            capture_method="automatic" if req.capture else "manual",
            metadata=req.resolve("metadata") or None,
            idempotency_key=req.resolve("idempotency_key"),
        )
        ref = PaymentRef(
            id=pi["id"],
            status=pi.get("status"),
            amount_minor=pi.get("amount"),
            currency=pi.get("currency"),
            provider=self.component_name,
            raw=pi,
        )
        return ref

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRef:
        stripe = self._client()
        pi = stripe.PaymentIntent.capture(
            payment_id,
            idempotency_key=idempotency_key,
        )
        ref = PaymentRef(
            id=pi["id"],
            status=pi.get("status"),
            amount_minor=pi.get("amount_received"),
            currency=pi.get("currency"),
            provider=self.component_name,
            raw=pi,
        )
        return ref

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRef:
        stripe = self._client()
        pi = stripe.PaymentIntent.cancel(
            payment_id,
            cancellation_reason=reason or None,
            idempotency_key=idempotency_key,
        )
        ref = PaymentRef(
            id=pi["id"],
            status=pi.get("status"),
            amount_minor=pi.get("amount"),
            currency=pi.get("currency"),
            provider=self.component_name,
            raw=pi,
        )
        return ref

    # ---------------------------------------------------------------- Subscriptions
    def _create_subscription(
        self, spec: SubscriptionSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        stripe = self._client()
        customer_id = self._require(spec, "customer_id")
        items = [
            {"price": item.price_id, "quantity": item.quantity} for item in spec.items
        ]
        if not items:
            raise ValueError("SubscriptionSpec.items must contain at least one item")
        sub = stripe.Subscription.create(
            customer=customer_id,
            items=items,
            trial_end=spec.resolve("trial_end"),
            collection_method=spec.resolve("collection_method"),
            metadata=spec.resolve("metadata") or None,
            idempotency_key=idempotency_key,
        )
        result = {
            "subscription_id": sub["id"],
            "status": sub.get("status"),
            "provider": self.component_name,
            "raw": sub,
        }
        return result

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        stripe = self._client()
        if at_period_end:
            sub = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True,
            )
        else:
            sub = stripe.Subscription.delete(subscription_id)
        result = {
            "subscription_id": subscription_id,
            "status": sub.get("status"),
            "provider": self.component_name,
            "raw": sub,
        }
        return result

    # ---------------------------------------------------------------- Invoicing
    def _create_invoice(
        self, spec: InvoiceSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        stripe = self._client()
        customer_id = self._require(spec, "customer_id")
        for item in spec.line_items:
            if item.price_id:
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    price=item.price_id,
                    quantity=item.quantity,
                )
            else:
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    amount=item.amount_minor or 0,
                    currency=(item.currency or "usd").lower(),
                    description=item.description or "",
                    quantity=item.quantity,
                )
        invoice = stripe.Invoice.create(
            customer=customer_id,
            collection_method=spec.resolve("collection_method"),
            days_until_due=spec.resolve("days_until_due"),
            metadata=spec.resolve("metadata") or None,
            idempotency_key=idempotency_key,
        )
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status"),
            "provider": self.component_name,
            "raw": invoice,
        }
        return result

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        stripe = self._client()
        invoice = stripe.Invoice.finalize_invoice(invoice_id)
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status"),
            "provider": self.component_name,
            "raw": invoice,
        }
        return result

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        stripe = self._client()
        invoice = stripe.Invoice.void_invoice(invoice_id)
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status"),
            "provider": self.component_name,
            "raw": invoice,
        }
        return result

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        stripe = self._client()
        invoice = stripe.Invoice.mark_uncollectible(invoice_id)
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status"),
            "provider": self.component_name,
            "raw": invoice,
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
        stripe = self._client()
        pi = stripe.PaymentIntent.create(
            amount=amount_minor,
            currency=currency.lower(),
            transfer_data={"destination": split_code_or_params["destination"]},
            application_fee_amount=split_code_or_params["application_fee_amount"],
            idempotency_key=idempotency_key,
        )
        result = {
            "payment_intent_id": pi["id"],
            "status": pi.get("status"),
            "provider": self.component_name,
            "raw": pi,
        }
        return result

    # ---------------------------------------------------------------- Risk
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        webhook = self._client().Webhook
        try:
            webhook.construct_event(
                payload=raw_body,
                sig_header=headers.get("Stripe-Signature", ""),
                secret=secret,
            )
            result = True
        except Exception:  # pragma: no cover - Stripe raises rich subclasses
            result = False
        return result

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        stripe = self._client()
        disputes = stripe.Dispute.list(limit=limit)
        data = disputes.get("data", []) if isinstance(disputes, Mapping) else []
        return cast(Sequence[Mapping[str, Any]], data)
