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
from swarmauri_core.billing import Operation


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

    # ---------------------------------------------------------------- Dispatch
    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        stripe = self._client()

        if operation is Operation.CREATE_PRODUCT:
            spec = cast(ProductSpec, payload["product_spec"])
            name = self._require(spec, "name")
            description = spec.resolve("description") or None
            metadata = spec.resolve("metadata") or None
            product = stripe.Product.create(
                name=name,
                description=description,
                metadata=metadata,
                idempotency_key=idempotency_key,
            )
            return ProductRef(
                id=product["id"],
                provider=self.component_name,
                name=product.get("name"),
                description=product.get("description"),
                metadata=product.get("metadata"),
                raw=product,
            )

        if operation is Operation.CREATE_PRICE:
            product_ref = cast(ProductRef, payload["product"])
            spec = cast(PriceSpec, payload["price_spec"])
            currency = self._require(spec, "currency")
            amount = int(self._require(spec, "unit_amount_minor"))
            price = stripe.Price.create(
                product=product_ref.id,
                currency=str(currency).lower(),
                unit_amount=amount,
                nickname=spec.resolve("nickname"),
                metadata=spec.resolve("metadata") or None,
                idempotency_key=idempotency_key,
            )
            return PriceRef(
                id=price["id"],
                product_id=price.get("product"),
                currency=price.get("currency"),
                unit_amount_minor=price.get("unit_amount"),
                provider=self.component_name,
                raw=price,
            )

        if operation is Operation.CREATE_CHECKOUT:
            price = cast(PriceRef, payload["price"])
            request = cast(CheckoutRequest, payload["request"])
            success_url = self._require(request, "success_url")
            cancel_url = request.resolve("cancel_url") or success_url
            metadata = request.resolve("metadata") or None
            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[{"price": price.id, "quantity": request.quantity}],
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=request.resolve("customer_email"),
                metadata=metadata,
                idempotency_key=request.resolve("idempotency_key"),
            )
            return CheckoutIntentRef(
                id=session["id"],
                url=session.get("url"),
                provider=self.component_name,
                raw=session,
            )

        if operation is Operation.CREATE_PAYMENT_INTENT:
            req = cast(PaymentIntentRequest, payload["req"])
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
            return PaymentRef(
                id=pi["id"],
                status=pi.get("status"),
                amount_minor=pi.get("amount"),
                currency=pi.get("currency"),
                provider=self.component_name,
                raw=pi,
            )

        if operation is Operation.CAPTURE_PAYMENT:
            payment_id = cast(str, payload["payment_id"])
            pi = stripe.PaymentIntent.capture(
                payment_id,
                idempotency_key=idempotency_key,
            )
            return PaymentRef(
                id=pi["id"],
                status=pi.get("status"),
                amount_minor=pi.get("amount_received"),
                currency=pi.get("currency"),
                provider=self.component_name,
                raw=pi,
            )

        if operation is Operation.CANCEL_PAYMENT:
            payment_id = cast(str, payload["payment_id"])
            pi = stripe.PaymentIntent.cancel(
                payment_id,
                cancellation_reason=payload.get("reason") or None,
                idempotency_key=idempotency_key,
            )
            return PaymentRef(
                id=pi["id"],
                status=pi.get("status"),
                amount_minor=pi.get("amount"),
                currency=pi.get("currency"),
                provider=self.component_name,
                raw=pi,
            )

        if operation is Operation.CREATE_SUBSCRIPTION:
            spec = cast(SubscriptionSpec, payload["spec"])
            customer_id = self._require(spec, "customer_id")
            items = [
                {"price": item.price_id, "quantity": item.quantity}
                for item in spec.items
            ]
            if not items:
                raise ValueError(
                    "SubscriptionSpec.items must contain at least one item"
                )
            sub = stripe.Subscription.create(
                customer=customer_id,
                items=items,
                trial_end=spec.resolve("trial_end"),
                collection_method=spec.resolve("collection_method"),
                metadata=spec.resolve("metadata") or None,
                idempotency_key=idempotency_key,
            )
            return {
                "subscription_id": sub["id"],
                "status": sub.get("status"),
                "provider": self.component_name,
                "raw": sub,
            }

        if operation is Operation.CANCEL_SUBSCRIPTION:
            subscription_id = cast(str, payload["subscription_id"])
            at_period_end = bool(payload.get("at_period_end", True))
            if at_period_end:
                sub = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
            else:
                sub = stripe.Subscription.delete(subscription_id)
            return {
                "subscription_id": subscription_id,
                "status": sub.get("status"),
                "provider": self.component_name,
                "raw": sub,
            }

        if operation is Operation.CREATE_INVOICE:
            spec = cast(InvoiceSpec, payload["spec"])
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
            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status"),
                "provider": self.component_name,
                "raw": invoice,
            }

        if operation is Operation.FINALIZE_INVOICE:
            invoice_id = cast(str, payload["invoice_id"])
            invoice = stripe.Invoice.finalize_invoice(invoice_id)
            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status"),
                "provider": self.component_name,
                "raw": invoice,
            }

        if operation is Operation.VOID_INVOICE:
            invoice_id = cast(str, payload["invoice_id"])
            invoice = stripe.Invoice.void_invoice(invoice_id)
            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status"),
                "provider": self.component_name,
                "raw": invoice,
            }

        if operation is Operation.MARK_UNCOLLECTIBLE:
            invoice_id = cast(str, payload["invoice_id"])
            invoice = stripe.Invoice.mark_uncollectible(invoice_id)
            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status"),
                "provider": self.component_name,
                "raw": invoice,
            }

        if operation is Operation.CREATE_SPLIT:
            spec = cast(SplitSpec, payload["spec"])
            return {
                "split": spec.model_dump(mode="json"),
                "provider": self.component_name,
            }

        if operation is Operation.CHARGE_WITH_SPLIT:
            amount_minor = int(payload["amount_minor"])
            currency = cast(str, payload["currency"])
            split_params = cast(Mapping[str, Any], payload["split"])
            pi = stripe.PaymentIntent.create(
                amount=amount_minor,
                currency=currency.lower(),
                transfer_data={"destination": split_params["destination"]},
                application_fee_amount=split_params["application_fee_amount"],
                idempotency_key=idempotency_key,
            )
            return {
                "payment_intent_id": pi["id"],
                "status": pi.get("status"),
                "provider": self.component_name,
                "raw": pi,
            }

        if operation is Operation.VERIFY_WEBHOOK_SIGNATURE:
            raw_body = cast(bytes, payload["raw_body"])
            headers = cast(Mapping[str, str], payload["headers"])
            secret = cast(str, payload["secret"])
            webhook = self._client().Webhook
            try:
                webhook.construct_event(
                    payload=raw_body,
                    sig_header=headers.get("Stripe-Signature", ""),
                    secret=secret,
                )
                return True
            except Exception:  # pragma: no cover - Stripe raises rich subclasses
                return False

        if operation is Operation.LIST_DISPUTES:
            disputes = stripe.Dispute.list(limit=payload.get("limit", 50))
            data = disputes.get("data", []) if isinstance(disputes, Mapping) else []
            return cast(Sequence[Mapping[str, Any]], data)

        raise NotImplementedError(f"Operation {operation} is not supported by Stripe")
