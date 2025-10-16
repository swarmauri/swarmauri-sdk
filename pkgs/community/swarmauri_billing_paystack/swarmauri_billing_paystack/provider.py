"""Paystack billing provider implementation."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, cast

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
from swarmauri_core.billing import Operation


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
    """Billing provider built on the ``paystackapi`` client."""

    component_name: str = "paystack"
    secret_key: SecretStr = Field(repr=False)
    _tx: Any = PrivateAttr(default=None)
    _product: Any = PrivateAttr(default=None)
    _sub: Any = PrivateAttr(default=None)
    _invoice: Any = PrivateAttr(default=None)
    _split: Any = PrivateAttr(default=None)

    # ------------------------------------------------------------------ Client
    def _ensure(self) -> None:
        if self._tx is not None:
            return
        from paystackapi.invoice import Invoice
        from paystackapi.paystack import Paystack
        from paystackapi.product import Product
        from paystackapi.split import Split
        from paystackapi.subscription import Subscription
        from paystackapi.transaction import Transaction

        Paystack.SECRET_KEY = self.secret_key.get_secret_value()
        self._tx = Transaction
        self._product = Product
        self._sub = Subscription
        self._invoice = Invoice
        self._split = Split

    @staticmethod
    def _require(spec: Any, field: str) -> Any:
        resolver = getattr(spec, "resolve", None)
        value = resolver(field) if callable(resolver) else getattr(spec, field, None)
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
        self._ensure()

        if operation is Operation.CREATE_PRODUCT:
            spec = cast(ProductSpec, payload["product_spec"])
            name = spec.resolve("name") or "Unnamed Product"
            description = spec.resolve("description") or ""
            resp = self._product.create(
                name=name,
                description=description,
                price=0,
                currency="NGN",
            )
            if not resp.get("status"):
                raise RuntimeError(resp.get("message", "product create failed"))
            data = resp["data"]
            return ProductRef(
                id=str(data["id"]),
                provider=self.component_name,
                name=data.get("name"),
                description=data.get("description"),
                raw=resp,
            )

        if operation is Operation.CREATE_PRICE:
            product = cast(ProductRef, payload["product"])
            spec = cast(PriceSpec, payload["price_spec"])
            amount = int(spec.resolve("unit_amount_minor") or 0)
            currency = str(spec.resolve("currency") or "NGN").upper()
            nickname = spec.resolve("nickname") or f"{product.id}-sku"
            resp = self._product.create(
                name=nickname,
                description=nickname,
                price=amount,
                currency=currency,
            )
            if not resp.get("status"):
                raise RuntimeError(resp.get("message", "price create failed"))
            data = resp["data"]
            price_id = data.get("product_code") or str(data.get("id"))
            return PriceRef(
                id=price_id,
                product_id=product.id,
                currency=data.get("currency"),
                unit_amount_minor=data.get("price"),
                provider=self.component_name,
                raw=resp,
            )

        if operation is Operation.CREATE_CHECKOUT:
            price = cast(PriceRef, payload["price"])
            request = cast(CheckoutRequest, payload["request"])
            amount = price.unit_amount_minor or price.raw["data"].get("price")
            currency = price.currency or price.raw["data"].get("currency", "NGN")
            init = self._tx.initialize(
                reference=request.resolve("idempotency_key") or f"chk-{price.id}",
                amount=amount,
                currency=currency,
                email=request.resolve("customer_email") or "buyer@example.com",
                metadata={
                    "product_id": price.product_id,
                    "price_code": price.id,
                },
                callback_url=self._require(request, "success_url"),
            )
            if not init.get("status"):
                raise RuntimeError(init.get("message", "checkout init failed"))
            data = init["data"]
            return CheckoutIntentRef(
                id=data.get("reference"),
                url=data.get("authorization_url"),
                provider=self.component_name,
                raw=init,
            )

        if operation is Operation.CREATE_PAYMENT_INTENT:
            req = cast(PaymentIntentRequest, payload["req"])
            amount = int(req.resolve("amount_minor") or 0)
            currency = str(req.resolve("currency") or "NGN").upper()
            init = self._tx.initialize(
                reference=req.resolve("idempotency_key") or "ref",
                amount=amount,
                currency=currency,
                email="buyer@example.com",
                metadata=req.resolve("metadata") or {},
            )
            if not init.get("status"):
                raise RuntimeError(init.get("message", "payment init failed"))
            data = init["data"]
            return PaymentRef(
                id=data.get("reference"),
                status="initialized",
                amount_minor=amount,
                currency=currency,
                provider=self.component_name,
                raw=init,
            )

        if operation is Operation.CAPTURE_PAYMENT:
            payment_id = cast(str, payload["payment_id"])
            return PaymentRef(
                id=payment_id,
                status="not_applicable",
                provider=self.component_name,
                raw=None,
            )

        if operation is Operation.CANCEL_PAYMENT:
            payment_id = cast(str, payload["payment_id"])
            return PaymentRef(
                id=payment_id,
                status="canceled_requested",
                provider=self.component_name,
                raw=None,
            )

        if operation is Operation.CREATE_SUBSCRIPTION:
            spec = cast(SubscriptionSpec, payload["spec"])
            if not spec.items:
                raise ValueError(
                    "SubscriptionSpec.items must contain at least one entry"
                )
            authorization = spec.resolve("metadata", {}).get("authorization")
            sub = self._sub.create(
                customer=spec.resolve("customer_id"),
                plan=spec.items[0].price_id,
                authorization=authorization,
            )
            if not sub.get("status"):
                raise RuntimeError(sub.get("message", "subscription failed"))
            data = sub["data"]
            return {
                "subscription_code": data.get("subscription_code"),
                "status": sub.get("message"),
                "provider": self.component_name,
                "raw": sub,
            }

        if operation is Operation.CANCEL_SUBSCRIPTION:
            subscription_id = cast(str, payload["subscription_id"])
            res = self._sub.disable(code=subscription_id, token=None)
            return {
                "subscription_code": subscription_id,
                "status": res.get("message", "disabled"),
                "provider": self.component_name,
                "raw": res,
            }

        if operation is Operation.CREATE_INVOICE:
            spec = cast(InvoiceSpec, payload["spec"])
            total_amount = sum((item.amount_minor or 0) for item in spec.line_items)
            inv = self._invoice.create(
                customer=spec.resolve("customer_id"),
                amount=total_amount,
                currency="NGN",
                due_date=None,
                description="Invoice",
            )
            if not inv.get("status"):
                raise RuntimeError(inv.get("message", "invoice create failed"))
            data = inv["data"]
            return {
                "invoice_id": data.get("invoice_code"),
                "status": "created",
                "provider": self.component_name,
                "raw": inv,
            }

        if operation is Operation.FINALIZE_INVOICE:
            invoice_id = cast(str, payload["invoice_id"])
            return {
                "invoice_id": invoice_id,
                "status": "finalized",
                "provider": self.component_name,
                "raw": None,
            }

        if operation is Operation.VOID_INVOICE:
            invoice_id = cast(str, payload["invoice_id"])
            res = self._invoice.notify(invoice_code=invoice_id)
            return {
                "invoice_id": invoice_id,
                "status": "void_requested",
                "provider": self.component_name,
                "raw": res,
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
            entries = [
                {"subaccount": entry.account, "share": entry.share}
                for entry in spec.entries
            ]
            sp = self._split.create(
                name=spec.resolve("name") or "Split",
                type=spec.resolve("type") or "percentage",
                currency=str(spec.resolve("currency") or "NGN").upper(),
                subaccounts=entries,
                bearer_type="account",
                bearer_subaccount=None,
            )
            if not sp.get("status"):
                raise RuntimeError(sp.get("message", "split create failed"))
            data = sp["data"]
            return {
                "split_code": data.get("split_code"),
                "provider": self.component_name,
                "raw": sp,
            }

        if operation is Operation.CHARGE_WITH_SPLIT:
            amount_minor = int(payload["amount_minor"])
            currency = str(payload["currency"] or "NGN").upper()
            split = cast(Mapping[str, Any], payload["split"])
            init = self._tx.initialize(
                reference=idempotency_key,
                amount=amount_minor,
                currency=currency,
                email="buyer@example.com",
                split_code=split["split_code"],
            )
            if not init.get("status"):
                raise RuntimeError(init.get("message", "split charge failed"))
            data = init["data"]
            return {
                "reference": data.get("reference"),
                "authorization_url": data.get("authorization_url"),
                "provider": self.component_name,
                "raw": init,
            }

        if operation is Operation.VERIFY_WEBHOOK_SIGNATURE:
            import hashlib
            import hmac

            raw_body = cast(bytes, payload["raw_body"])
            headers = cast(Mapping[str, str], payload["headers"])
            secret = cast(str, payload["secret"])
            signature = headers.get("X-Paystack-Signature", "")
            digest = hmac.new(secret.encode(), raw_body, hashlib.sha512).hexdigest()
            return hmac.compare_digest(digest, signature)

        if operation is Operation.LIST_DISPUTES:
            from paystackapi.dispute import Dispute

            res = Dispute.list()
            if isinstance(res, Mapping):
                return cast(Sequence[Mapping[str, Any]], res.get("data", []))
            return tuple()

        raise NotImplementedError(f"Operation {operation} is not supported by Paystack")


__all__ = ["PaystackBillingProvider"]
