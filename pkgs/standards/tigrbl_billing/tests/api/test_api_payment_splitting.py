import pytest

from tigrbl_billing.api import api_payment_splitting


@pytest.mark.asyncio
async def test_refund_application_fee_marks_refunded(uvicorn_client):
    async with uvicorn_client(api_payment_splitting.app) as client:
        fee = await client.post(
            "/application_fee",
            json={"stripe_application_fee_id": "fee_123", "refunded": False},
        )
        fee_id = fee.json()["data"]["id"]

        refund = await client.post(
            "/application_fee/refund_app_fee",
            json={"application_fee_id": fee_id},
        )
        assert refund.status_code == 200

        record = (await client.get("/application_fee")).json()["items"][0]
        assert record["refunded"] is True
