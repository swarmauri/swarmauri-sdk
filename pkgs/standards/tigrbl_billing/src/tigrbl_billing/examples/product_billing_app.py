"""Example application showing a product-based billing flow."""

from __future__ import annotations

from typing import Any, Dict

import httpx

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing import ops as billing_ops
from tigrbl_billing.tables.checkout_session import CheckoutSession
from tigrbl_billing.tables.customer import Customer
from tigrbl_billing.tables.payment_intent import PaymentIntent
from tigrbl_billing.tables.price import Price
from tigrbl_billing.tables.product import Product
from tigrbl_billing.tables.refund import Refund

_REQUIRED_OPS = (
    billing_ops.create_or_link_customer,
    billing_ops.attach_payment_method,
    billing_ops.capture_payment_intent,
    billing_ops.cancel_payment_intent,
    billing_ops.refund_application_fee,
    billing_ops.sync_objects,
)


def build_product_billing_app(async_mode: bool = True) -> TigrblApp:
    """Create a :class:`~tigrbl.TigrblApp` preloaded with product billing tables."""

    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models(
        [
            Product,
            Price,
            Customer,
            CheckoutSession,
            PaymentIntent,
            Refund,
        ]
    )
    return app


async def run_product_billing_flow(app: TigrblApp | None = None) -> Dict[str, Any]:
    """Execute a simple product checkout, payment, and refund flow."""

    app = app or build_product_billing_app(async_mode=True)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://product-billing.test"
    ) as client:
        product_payload = {
            "external_id": "prod_simple_suite",
            "name": "Simple Suite",
            "description": "Bundled productivity features",
            "metadata": {"segment": "smb"},
        }
        product_response = await client.post("/product", json=product_payload)
        product_id = product_response.json()["data"]["id"]

        price_payload = {
            "external_id": "price_simple_suite_monthly",
            "product_id": product_id,
            "currency": "usd",
            "billing_scheme": "flat",
            "unit_amount": 4999,
            "usage_type": "licensed",
            "recurring_interval": "month",
            "recurring_count": 1,
            "metadata": {"plan": "monthly"},
        }
        price_response = await client.post("/price", json=price_payload)
        price_id = price_response.json()["data"]["id"]

        customer_payload = {
            "external_id": "cus_simple_suite",
            "email": "owner@example.com",
            "name": "Simple Suite Owner",
            "metadata": {"company": "Simple Suite LLC"},
        }
        customer_response = await client.post("/customer", json=customer_payload)
        customer_id = customer_response.json()["data"]["id"]

        checkout_payload = {
            "external_id": "cs_simple_suite_trial",
            "mode": "subscription",
            "customer_id": customer_id,
            "status": "open",
            "success_url": "https://example.com/thanks",
            "cancel_url": "https://example.com/cancel",
            "line_items": {
                "items": [
                    {
                        "price_id": price_id,
                        "quantity": 1,
                        "unit_amount": 4999,
                    }
                ]
            },
            "metadata": {"campaign": "launch"},
        }
        checkout_response = await client.post(
            "/checkout_session", json=checkout_payload
        )
        checkout_id = checkout_response.json()["data"]["id"]

        payment_intent_payload = {
            "external_id": "pi_simple_suite",
            "customer_id": customer_id,
            "currency": "usd",
            "amount": 4999,
            "status": "succeeded",
            "capture_method": "automatic",
            "payment_method_types": ["card"],
            "metadata": {"checkout_session_id": checkout_id},
        }
        payment_intent_response = await client.post(
            "/payment_intent", json=payment_intent_payload
        )
        payment_intent_id = payment_intent_response.json()["data"]["id"]

        refund_payload = {
            "external_id": "re_simple_suite_partial",
            "payment_intent_id": payment_intent_id,
            "amount": 1999,
            "status": "succeeded",
            "reason": "requested_by_customer",
        }
        refund_response = await client.post("/refund", json=refund_payload)
        refund_id = refund_response.json()["data"]["id"]

        product_record = (await client.get(f"/product/{product_id}")).json()
        price_record = (await client.get(f"/price/{price_id}")).json()
        checkout_record = (await client.get(f"/checkout_session/{checkout_id}")).json()
        payment_intent_record = (
            await client.get(f"/payment_intent/{payment_intent_id}")
        ).json()
        refund_record = (await client.get(f"/refund/{refund_id}")).json()

        return {
            "product": product_record,
            "price": price_record,
            "checkout": checkout_record,
            "payment_intent": payment_intent_record,
            "refund": refund_record,
        }
