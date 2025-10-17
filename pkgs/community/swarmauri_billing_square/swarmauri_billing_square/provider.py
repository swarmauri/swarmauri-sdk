"""Square billing provider implementation."""

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


class SquareBillingProvider(
    ProductsPricesMixin,
    HostedCheckoutMixin,
    OnlinePaymentsMixin,
    SubscriptionsMixin,
    InvoicingMixin,
    MarketplaceMixin,
    RiskMixin,
    BillingProviderBase,
):
    """Concrete billing provider backed by the Square Python SDK."""

    component_name: str = "square"
    access_token: SecretStr = Field(repr=False)
    environment: str = Field(default="sandbox", description="Square environment")
    location_id: str = Field(..., description="Default Square location identifier")
    _client: Any = PrivateAttr(default=None)

    # ------------------------------------------------------------------ Client
    def _sq(self) -> Any:
        if self._client is None:
            from square.client import Client

            self._client = Client(
                access_token=self.access_token.get_secret_value(),
                environment=self.environment,
            )
        return self._client

    @staticmethod
    def _raise_if_error(response: Any) -> None:
        if hasattr(response, "is_error") and response.is_error():
            raise RuntimeError(str(response.errors))

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
        sq = self._sq()
        name = self._require(product_spec, "name")
        description = product_spec.resolve("description") or ""
        tmp_id = f"#{idempotency_key}-item"
        response = sq.catalog.upsert_catalog_object(
            body={
                "idempotency_key": idempotency_key,
                "object": {
                    "id": tmp_id,
                    "type": "ITEM",
                    "present_at_all_locations": True,
                    "item_data": {
                        "name": name,
                        "description": description,
                    },
                },
            }
        )
        self._raise_if_error(response)
        catalog_object = response.body["catalog_object"]
        ref = ProductRef(
            id=catalog_object["id"],
            provider=self.component_name,
            name=catalog_object.get("item_data", {}).get("name"),
            description=catalog_object.get("item_data", {}).get("description"),
            raw=response.body,
        )
        return ref

    def _create_price(
        self,
        product: ProductRef,
        price_spec: PriceSpec,
        *,
        idempotency_key: str,
    ) -> PriceRef:
        sq = self._sq()
        amount = int(self._require(price_spec, "unit_amount_minor"))
        currency = str(self._require(price_spec, "currency")).upper()
        nickname = price_spec.resolve("nickname") or "Default"
        tmp_id = f"#{idempotency_key}-var"
        response = sq.catalog.upsert_catalog_object(
            body={
                "idempotency_key": idempotency_key,
                "object": {
                    "id": tmp_id,
                    "type": "ITEM_VARIATION",
                    "present_at_all_locations": True,
                    "item_variation_data": {
                        "item_id": product.id,
                        "name": nickname,
                        "pricing_type": "FIXED_PRICING",
                        "price_money": {
                            "amount": amount,
                            "currency": currency,
                        },
                    },
                },
            }
        )
        self._raise_if_error(response)
        mappings = response.body.get("id_mappings", [])
        object_id = next(
            (m["object_id"] for m in mappings if m["client_object_id"] == tmp_id),
            None,
        )
        if object_id is None:
            raise RuntimeError("Square did not return a mapped price identifier")
        ref = PriceRef(
            id=object_id,
            product_id=product.id,
            currency=currency.lower(),
            unit_amount_minor=amount,
            provider=self.component_name,
            raw=response.body,
        )
        return ref

    # ---------------------------------------------------------------- Hosted Checkout
    def _create_checkout(
        self, price: PriceRef, request: CheckoutRequest
    ) -> CheckoutIntentRef:
        sq = self._sq()
        response = sq.checkout.create_payment_link(
            body={
                "idempotency_key": request.resolve("idempotency_key")
                or f"chk-{price.id}",
                "order": {
                    "location_id": self.location_id,
                    "line_items": [
                        {
                            "catalog_object_id": price.id,
                            "quantity": str(request.quantity),
                        }
                    ],
                },
                "checkout_options": {
                    "redirect_url": self._require(request, "success_url"),
                },
            }
        )
        self._raise_if_error(response)
        payment_link = response.body["payment_link"]
        intent = CheckoutIntentRef(
            id=payment_link["id"],
            url=payment_link.get("url"),
            provider=self.component_name,
            raw=response.body,
        )
        return intent

    # ---------------------------------------------------------------- Online Payments
    def _create_payment_intent(self, req: PaymentIntentRequest) -> PaymentRef:
        sq = self._sq()
        amount = int(self._require(req, "amount_minor"))
        currency = str(self._require(req, "currency")).upper()
        response = sq.payments.create(
            source_id=req.resolve("payment_method_id") or "EXTERNAL",
            idempotency_key=req.resolve("idempotency_key"),
            amount_money={"amount": amount, "currency": currency},
            autocomplete=req.capture,
            location_id=self.location_id,
        )
        self._raise_if_error(response)
        payment = response.body["payment"]
        ref = PaymentRef(
            id=payment["id"],
            status=payment.get("status"),
            amount_minor=payment.get("amount_money", {}).get("amount"),
            currency=payment.get("amount_money", {}).get("currency"),
            provider=self.component_name,
            raw=response.body,
        )
        return ref

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRef:
        sq = self._sq()
        response = sq.payments.complete_payment(payment_id)
        self._raise_if_error(response)
        payment = response.body["payment"]
        ref = PaymentRef(
            id=payment["id"],
            status=payment.get("status"),
            amount_minor=payment.get("amount_money", {}).get("amount"),
            currency=payment.get("amount_money", {}).get("currency"),
            provider=self.component_name,
            raw=response.body,
        )
        return ref

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRef:
        sq = self._sq()
        response = sq.payments.cancel_payment(payment_id)
        self._raise_if_error(response)
        payment = response.body["payment"]
        ref = PaymentRef(
            id=payment["id"],
            status=payment.get("status"),
            amount_minor=payment.get("amount_money", {}).get("amount"),
            currency=payment.get("amount_money", {}).get("currency"),
            provider=self.component_name,
            raw=response.body,
        )
        return ref

    # ---------------------------------------------------------------- Subscriptions
    def _create_subscription(
        self, spec: SubscriptionSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        sq = self._sq()
        plan_id = spec.items[0].price_id
        response = sq.subscriptions.create_subscription(
            idempotency_key=idempotency_key,
            location_id=self.location_id,
            customer_id=self._require(spec, "customer_id"),
            plan_id=plan_id,
        )
        self._raise_if_error(response)
        subscription = response.body["subscription"]
        result = {
            "subscription_id": subscription["id"],
            "status": subscription.get("status"),
            "provider": self.component_name,
            "raw": response.body,
        }
        return result

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        sq = self._sq()
        if at_period_end:
            response = sq.subscriptions.update_subscription(
                subscription_id,
                body={
                    "subscription": {
                        "canceled_date": None,
                        "status": "CANCEL_PENDING",
                    }
                },
            )
        else:
            response = sq.subscriptions.cancel_subscription(subscription_id)
        self._raise_if_error(response)
        subscription = response.body.get("subscription") or {}
        result = {
            "subscription_id": subscription_id,
            "status": subscription.get("status", "CANCELED"),
            "provider": self.component_name,
            "raw": response.body,
        }
        return result

    # ---------------------------------------------------------------- Invoicing
    def _create_invoice(
        self, spec: InvoiceSpec, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        sq = self._sq()
        response = sq.invoices.create_invoice(
            invoice={
                "location_id": self.location_id,
                "primary_recipient": {
                    "customer_id": self._require(spec, "customer_id")
                },
                "payment_requests": [
                    {
                        "request_type": "BALANCE",
                        **(
                            {"due_date": f"+{spec.resolve('days_until_due')}d"}
                            if spec.resolve("collection_method") == "send_invoice"
                            else {}
                        ),
                    }
                ],
            },
            idempotency_key=idempotency_key,
        )
        self._raise_if_error(response)
        invoice = response.body["invoice"]
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status"),
            "provider": self.component_name,
            "raw": response.body,
        }
        return result

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        sq = self._sq()
        response = sq.invoices.publish_invoice(
            invoice_id=invoice_id, idempotency_key=f"pub-{invoice_id}"
        )
        self._raise_if_error(response)
        invoice = response.body["invoice"]
        result = {
            "invoice_id": invoice["id"],
            "status": invoice.get("status"),
            "provider": self.component_name,
            "raw": response.body,
        }
        return result

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        sq = self._sq()
        response = sq.invoices.cancel_invoice(
            invoice_id=invoice_id, idempotency_key=f"void-{invoice_id}"
        )
        self._raise_if_error(response)
        result = {
            "invoice_id": invoice_id,
            "status": "CANCELED",
            "provider": self.component_name,
            "raw": response.body,
        }
        return result

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        sq = self._sq()
        response = sq.invoices.cancel_invoice(
            invoice_id=invoice_id, idempotency_key=f"void-{invoice_id}"
        )
        self._raise_if_error(response)
        result = {
            "invoice_id": invoice_id,
            "status": "CANCELED",
            "provider": self.component_name,
            "raw": response.body,
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
        sq = self._sq()
        response = sq.payments.create(
            source_id=split_code_or_params.get("source_id", "EXTERNAL"),
            idempotency_key=idempotency_key,
            amount_money={"amount": amount_minor, "currency": currency.upper()},
            app_fee_money={
                "amount": split_code_or_params["app_fee_amount"],
                "currency": currency.upper(),
            },
            location_id=self.location_id,
            autocomplete=True,
        )
        self._raise_if_error(response)
        payment = response.body["payment"]
        result = {
            "payment_id": payment["id"],
            "status": payment.get("status"),
            "provider": self.component_name,
            "raw": response.body,
        }
        return result

    # ---------------------------------------------------------------- Risk
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        return True

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        sq = self._sq()
        response = sq.disputes.list_disputes()
        self._raise_if_error(response)
        disputes = response.body.get("disputes", [])
        return cast(Sequence[Mapping[str, Any]], disputes)


__all__ = ["SquareBillingProvider"]
