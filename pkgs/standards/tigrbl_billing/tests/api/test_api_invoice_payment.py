import pytest

from tigrbl_billing.api import api_invoice_payment


@pytest.mark.asyncio
async def test_finalize_and_void_invoice(uvicorn_client):
    async with uvicorn_client(api_invoice_payment.app) as client:
        created = await client.post(
            "/invoice",
            json={"status": "DRAFT", "line_items": []},
        )
        invoice_id = created.json()["data"]["id"]

        finalize = await client.post(
            "/invoice/finalize",
            json={"invoice_id": invoice_id, "line_items": [{"amount": 1000}]},
        )
        assert finalize.status_code == 200

        void = await client.post("/invoice/void", json={"invoice_id": invoice_id})
        assert void.status_code == 200

        read = await client.get(f"/invoice/{invoice_id}")
        invoice = read.json()
        assert invoice["status"] == "VOID"
        assert invoice["line_items"][0]["amount"] == 1000


@pytest.mark.asyncio
async def test_capture_and_cancel_payment_intent(uvicorn_client):
    async with uvicorn_client(api_invoice_payment.app) as client:
        created = await client.post(
            "/payment_intent",
            json={"status": "requires_payment_method"},
        )
        intent_id = created.json()["data"]["id"]

        capture = await client.post(
            "/payment_intent/capture", json={"payment_intent_id": intent_id}
        )
        assert capture.status_code == 200

        cancel = await client.post(
            "/payment_intent/cancel", json={"payment_intent_id": intent_id}
        )
        assert cancel.status_code == 200

        record = (await client.get(f"/payment_intent/{intent_id}")).json()
        assert record["status"] == "CANCELED"
