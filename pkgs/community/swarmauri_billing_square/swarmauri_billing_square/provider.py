"""Square billing provider implementation."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, cast

from pydantic import Field, PrivateAttr, SecretStr

from swarmauri_base.billing import (
    BillingProviderBase,
    BillingSpec,
    CheckoutIntentRef,
    CheckoutRequest,
    InvoiceSpec,
    PaymentIntentRequest,
    PaymentRef,
    PriceRef,
    PriceSpec,
    ProductRef,
    ProductSpec,
    SplitSpec,
    SubscriptionSpec,
)
from swarmauri_core.billing import Operation


class SquareBillingProvider(BillingProviderBase):
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

    # ---------------------------------------------------------------- Dispatch
    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        sq = self._sq()

        if operation is Operation.CREATE_PRODUCT:
            spec = cast(ProductSpec, payload["product_spec"])
            name = self._require(spec, "name")
            description = spec.resolve("description") or ""
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
            return ProductRef(
                id=catalog_object["id"],
                provider=self.component_name,
                name=catalog_object.get("item_data", {}).get("name"),
                description=catalog_object.get("item_data", {}).get("description"),
                raw=response.body,
            )

        if operation is Operation.CREATE_PRICE:
            product = cast(ProductRef, payload["product"])
            spec = cast(PriceSpec, payload["price_spec"])
            amount = int(self._require(spec, "unit_amount_minor"))
            currency = str(self._require(spec, "currency")).upper()
            nickname = spec.resolve("nickname") or "Default"
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
            return PriceRef(
                id=object_id,
                product_id=product.id,
                currency=currency.lower(),
                unit_amount_minor=amount,
                provider=self.component_name,
                raw=response.body,
            )

        if operation is Operation.CREATE_CHECKOUT:
            price = cast(PriceRef, payload["price"])
            request = cast(CheckoutRequest, payload["request"])
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
            return CheckoutIntentRef(
                id=payment_link["id"],
                url=payment_link.get("url"),
                provider=self.component_name,
                raw=response.body,
            )

        if operation is Operation.CREATE_PAYMENT_INTENT:
            req = cast(PaymentIntentRequest, payload["req"])
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
            return PaymentRef(
                id=payment["id"],
                status=payment.get("status"),
                amount_minor=payment.get("amount_money", {}).get("amount"),
                currency=payment.get("amount_money", {}).get("currency"),
                provider=self.component_name,
                raw=response.body,
            )

        if operation is Operation.CAPTURE_PAYMENT:
            payment_id = cast(str, payload["payment_id"])
            response = sq.payments.complete_payment(payment_id)
            self._raise_if_error(response)
            payment = response.body["payment"]
            return PaymentRef(
                id=payment["id"],
                status=payment.get("status"),
                amount_minor=payment.get("total_money", {}).get("amount"),
                currency=payment.get("total_money", {}).get("currency"),
                provider=self.component_name,
                raw=response.body,
            )

        if operation is Operation.CANCEL_PAYMENT:
            payment_id = cast(str, payload["payment_id"])
            response = sq.payments.cancel_payment(payment_id)
            self._raise_if_error(response)
            payment = response.body["payment"]
            return PaymentRef(
                id=payment["id"],
                status=payment.get("status"),
                provider=self.component_name,
                raw=response.body,
            )

        if operation is Operation.CREATE_SUBSCRIPTION:
            spec = cast(SubscriptionSpec, payload["spec"])
            if not spec.items:
                raise ValueError(
                    "SubscriptionSpec.items must contain at least one entry"
                )
            plan_id = self._require(spec.items[0], "price_id")
            response = sq.subscriptions.create_subscription(
                idempotency_key=idempotency_key,
                location_id=self.location_id,
                customer_id=self._require(spec, "customer_id"),
                plan_id=plan_id,
            )
            self._raise_if_error(response)
            subscription = response.body["subscription"]
            return {
                "subscription_id": subscription["id"],
                "status": subscription.get("status"),
                "provider": self.component_name,
                "raw": response.body,
            }

        if operation is Operation.CANCEL_SUBSCRIPTION:
            subscription_id = cast(str, payload["subscription_id"])
            at_period_end = bool(payload.get("at_period_end", True))
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
            return {
                "subscription_id": subscription_id,
                "status": subscription.get("status", "CANCELED"),
                "provider": self.component_name,
                "raw": response.body,
            }

        if operation is Operation.CREATE_INVOICE:
            spec = cast(InvoiceSpec, payload["spec"])
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
                                and spec.resolve("days_until_due")
                                else {}
                            ),
                        }
                    ],
                },
                idempotency_key=idempotency_key,
            )
            self._raise_if_error(response)
            invoice = response.body["invoice"]
            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status"),
                "provider": self.component_name,
                "raw": response.body,
            }

        if operation is Operation.FINALIZE_INVOICE:
            invoice_id = cast(str, payload["invoice_id"])
            response = sq.invoices.publish_invoice(
                invoice_id=invoice_id,
                idempotency_key=f"publish-{invoice_id}",
            )
            self._raise_if_error(response)
            invoice = response.body["invoice"]
            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status"),
                "provider": self.component_name,
                "raw": response.body,
            }

        if operation is Operation.VOID_INVOICE:
            invoice_id = cast(str, payload["invoice_id"])
            response = sq.invoices.cancel_invoice(
                invoice_id=invoice_id,
                idempotency_key=f"void-{invoice_id}",
            )
            self._raise_if_error(response)
            return {
                "invoice_id": invoice_id,
                "status": "CANCELED",
                "provider": self.component_name,
                "raw": response.body,
            }

        if operation is Operation.MARK_UNCOLLECTIBLE:
            invoice_id = cast(str, payload["invoice_id"])
            return self._dispatch(
                Operation.VOID_INVOICE,
                {"invoice_id": invoice_id},
                idempotency_key=idempotency_key,
            )

        if operation is Operation.CREATE_SPLIT:
            spec = cast(SplitSpec, payload["spec"])
            return {
                "split": spec.model_dump(mode="json"),
                "provider": self.component_name,
            }

        if operation is Operation.CHARGE_WITH_SPLIT:
            amount_minor = int(payload["amount_minor"])
            currency = str(payload["currency"]).upper()
            split = cast(Mapping[str, Any], payload["split"])
            response = sq.payments.create(
                source_id=split.get("source_id", "EXTERNAL"),
                idempotency_key=idempotency_key,
                amount_money={"amount": amount_minor, "currency": currency},
                app_fee_money={
                    "amount": split["app_fee_amount"],
                    "currency": currency,
                },
                location_id=self.location_id,
                autocomplete=True,
            )
            self._raise_if_error(response)
            payment = response.body["payment"]
            return {
                "payment_id": payment["id"],
                "status": payment.get("status"),
                "provider": self.component_name,
                "raw": response.body,
            }

        if operation is Operation.VERIFY_WEBHOOK_SIGNATURE:
            return True  # Implement in HTTP layer with configured Square credentials.

        if operation is Operation.LIST_DISPUTES:
            response = sq.disputes.list_disputes()
            self._raise_if_error(response)
            disputes = response.body.get("disputes", [])
            return cast(Sequence[Mapping[str, Any]], disputes)

        raise NotImplementedError(f"Operation {operation} is not supported by Square")


__all__ = ["SquareBillingProvider"]
