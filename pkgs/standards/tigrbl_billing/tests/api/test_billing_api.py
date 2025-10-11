import pytest

from tigrbl_billing.api import billing_api


@pytest.mark.asyncio
async def test_customer_account_operations(uvicorn_client):
    async with uvicorn_client(billing_api.app) as client:
        customer = await client.post(
            "/customer/create_or_link",
            json={"email": "billing@example.com", "name": "Billing"},
        )
        assert customer.status_code == 200
        customer_id = customer.json()["data"]["id"]

        attach = await client.post(
            "/customer/attach_payment_method",
            json={"customer_id": customer_id, "payment_method_ref": "pm_bill"},
        )
        assert attach.status_code == 200

        record = (await client.get(f"/customer/{customer_id}")).json()
        assert record["default_payment_method_ref"] == "pm_bill"


@pytest.mark.asyncio
async def test_subscription_and_seat_workflow(uvicorn_client):
    async with uvicorn_client(billing_api.app) as client:
        subscription = await client.post(
            "/subscription/start",
            json={"customer_id": "cust-bill", "items": []},
        )
        subscription_id = subscription.json()["data"]["id"]

        assign = await client.post(
            "/seat_allocation/assign",
            json={
                "subscription_item_id": subscription_id,
                "subject_ref": "user-seat",
            },
        )
        seat_id = assign.json()["data"]["id"]

        release = await client.post(
            "/seat_allocation/release", json={"seat_allocation_id": seat_id}
        )
        assert release.status_code == 200

        sub_record = (await client.get(f"/subscription/{subscription_id}")).json()
        assert sub_record["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_invoice_and_payment_intent_flow(uvicorn_client):
    async with uvicorn_client(billing_api.app) as client:
        invoice = await client.post(
            "/invoice", json={"status": "DRAFT", "line_items": []}
        )
        invoice_id = invoice.json()["data"]["id"]

        await client.post(
            "/invoice/finalize", json={"invoice_id": invoice_id, "line_items": []}
        )
        await client.post(
            "/invoice/mark_uncollectible", json={"invoice_id": invoice_id}
        )

        payment_intent = await client.post(
            "/payment_intent", json={"status": "requires_capture"}
        )
        intent_id = payment_intent.json()["data"]["id"]

        await client.post(
            "/payment_intent/capture", json={"payment_intent_id": intent_id}
        )
        final_intent = (await client.get(f"/payment_intent/{intent_id}")).json()
        assert final_intent["status"] == "SUCCEEDED"


@pytest.mark.asyncio
async def test_credit_and_top_off_operations(uvicorn_client):
    async with uvicorn_client(billing_api.app) as client:
        top_off = await client.post(
            "/customer_balance/request_top_off",
            json={"balance_id": "bal-main", "amount": 1000, "currency": "usd"},
        )
        assert top_off.status_code == 200

        grant = await client.post(
            "/credit_grant",
            json={"status": "PENDING", "revoke_amount": 0, "revoke_reason": None},
        )
        grant_id = grant.json()["data"]["id"]
        await client.post("/credit_grant/apply_grant", json={"grant_id": grant_id})

        charge = await client.post(
            "/usage_event/charge_credits",
            json={
                "usage_event_id": "evt-credit",
                "customer_id": "cust-bill",
                "feature_key": "credits",
                "quantity": 3,
                "currency": "usd",
            },
        )
        assert charge.status_code == 200

        ledger_entries = (await client.get("/usage_event")).json()["items"]
        assert ledger_entries[0]["direction"] == "DEBIT"
