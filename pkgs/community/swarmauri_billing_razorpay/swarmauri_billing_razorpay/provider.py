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

    # ---------------------------------------------------------------- Dispatch
    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        client = self._rz()

        if operation is Operation.CREATE_PRODUCT:
            spec = cast(ProductSpec, payload["product_spec"])
            name = self._require(spec, "name")
            description = spec.resolve("description") or spec.resolve("sku") or ""
            item = client.item.create(
                {
                    "name": name,
                    "description": description,
                    "amount": 0,
                    "currency": "INR",
                }
            )
            return ProductRef(
                id=item["id"],
                provider=self.component_name,
                name=item.get("name"),
                description=item.get("description"),
                raw=item,
            )

        if operation is Operation.CREATE_PRICE:
            product = cast(ProductRef, payload["product"])
            spec = cast(PriceSpec, payload["price_spec"])
            amount = int(self._require(spec, "unit_amount_minor"))
            currency = str(self._require(spec, "currency")).upper()
            nickname = spec.resolve("nickname") or f"{product.id}-price"
            priced = client.item.create(
                {
                    "name": nickname,
                    "amount": amount,
                    "currency": currency,
                    "description": nickname,
                }
            )
            return PriceRef(
                id=priced["id"],
                product_id=product.id,
                currency=priced.get("currency"),
                unit_amount_minor=priced.get("amount"),
                provider=self.component_name,
                raw=priced,
            )

        if operation is Operation.CREATE_CHECKOUT:
            price = cast(PriceRef, payload["price"])
            request = cast(CheckoutRequest, payload["request"])
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
            return CheckoutIntentRef(
                id=link["id"],
                url=link.get("short_url"),
                provider=self.component_name,
                raw=link,
            )

        if operation is Operation.CREATE_PAYMENT_INTENT:
            req = cast(PaymentIntentRequest, payload["req"])
            amount = int(self._require(req, "amount_minor"))
            currency = str(self._require(req, "currency")).upper()
            order = client.order.create(
                {
                    "amount": amount,
                    "currency": currency,
                    "receipt": req.resolve("idempotency_key") or "receipt",
                }
            )
            return PaymentRef(
                id=order["id"],
                status=order.get("status"),
                amount_minor=order.get("amount"),
                currency=order.get("currency"),
                provider=self.component_name,
                raw=order,
            )

        if operation is Operation.CAPTURE_PAYMENT:
            payment_id = cast(str, payload["payment_id"])
            payment = client.payment.capture(payment_id, data={"amount": None})
            return PaymentRef(
                id=payment["id"],
                status=payment.get("status"),
                provider=self.component_name,
                raw=payment,
            )

        if operation is Operation.CANCEL_PAYMENT:
            payment_id = cast(str, payload["payment_id"])
            payment = client.payment.refund(payment_id, data={"speed": "optimum"})
            return PaymentRef(
                id=payment["id"],
                status=payment.get("status", "refunded"),
                provider=self.component_name,
                raw=payment,
            )

        if operation is Operation.CREATE_SUBSCRIPTION:
            spec = cast(SubscriptionSpec, payload["spec"])
            if not spec.items:
                raise ValueError(
                    "SubscriptionSpec.items must contain at least one entry"
                )
            plan_id = self._require(spec.items[0], "price_id")
            subscription = client.subscription.create(
                {
                    "plan_id": plan_id,
                    "total_count": 999999,
                    "customer_notify": 1,
                }
            )
            return {
                "subscription_id": subscription["id"],
                "status": subscription.get("status"),
                "provider": self.component_name,
                "raw": subscription,
            }

        if operation is Operation.CANCEL_SUBSCRIPTION:
            subscription_id = cast(str, payload["subscription_id"])
            at_period_end = bool(payload.get("at_period_end", True))
            subscription = client.subscription.cancel(
                subscription_id,
                data={"cancel_at_cycle_end": at_period_end},
            )
            return {
                "subscription_id": subscription["id"],
                "status": subscription.get("status"),
                "provider": self.component_name,
                "raw": subscription,
            }

        if operation is Operation.CREATE_INVOICE:
            spec = cast(InvoiceSpec, payload["spec"])
            customer_ref = self._require(spec, "customer_id")
            customer_payload: Mapping[str, Any]
            if str(customer_ref).startswith("cust_"):
                customer_payload = {"id": customer_ref}
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
            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status"),
                "provider": self.component_name,
                "raw": invoice,
            }

        if operation is Operation.FINALIZE_INVOICE:
            invoice_id = cast(str, payload["invoice_id"])
            invoice = client.invoice.issue(invoice_id)
            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status"),
                "provider": self.component_name,
                "raw": invoice,
            }

        if operation is Operation.VOID_INVOICE:
            invoice_id = cast(str, payload["invoice_id"])
            invoice = client.invoice.cancel(invoice_id)
            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status", "cancelled"),
                "provider": self.component_name,
                "raw": invoice,
            }

        if operation is Operation.MARK_UNCOLLECTIBLE:
            invoice_id = cast(str, payload["invoice_id"])
            return {
                "invoice_id": invoice_id,
                "status": "uncollectible",
                "provider": self.component_name,
                "raw": None,
            }

        if operation is Operation.CREATE_SPLIT:
            spec = cast(SplitSpec, payload["spec"])
            return {
                "split": spec.model_dump(mode="json"),
                "provider": self.component_name,
            }

        if operation is Operation.CHARGE_WITH_SPLIT:
            split = cast(Mapping[str, Any], payload["split"])
            payment_id = split["payment_id"]
            transfers = client.payment.transfer(
                payment_id, data={"transfers": split["transfers"]}
            )
            return {
                "payment_id": payment_id,
                "transfers": transfers,
                "provider": self.component_name,
                "raw": transfers,
            }

        if operation is Operation.VERIFY_WEBHOOK_SIGNATURE:
            import hashlib
            import hmac

            raw_body = cast(bytes, payload["raw_body"])
            headers = cast(Mapping[str, str], payload["headers"])
            secret = cast(str, payload["secret"])
            signature = headers.get("X-Razorpay-Signature", "")
            digest = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
            return hmac.compare_digest(digest, signature)

        if operation is Operation.LIST_DISPUTES:
            settlements = client.payments.fetch_settlements()
            if isinstance(settlements, Mapping):
                return cast(Sequence[Mapping[str, Any]], settlements.get("items", []))
            return tuple()

        raise NotImplementedError(f"Operation {operation} is not supported by Razorpay")


__all__ = ["RazorpayBillingProvider"]
