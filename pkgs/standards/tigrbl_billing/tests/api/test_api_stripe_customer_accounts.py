import pytest

from tigrbl_billing.api import api_stripe_customer_accounts


@pytest.mark.asyncio
async def test_create_or_link_customer_and_attach_payment_method(uvicorn_client):
    async with uvicorn_client(api_stripe_customer_accounts.app) as client:
        create = await client.post(
            "/customer/create_or_link",
            json={
                "email": "user@example.com",
                "name": "User",
                "tax_exempt": "reverse",
            },
        )
        assert create.status_code == 200
        customer_id = create.json()["data"]["id"]

        attach = await client.post(
            "/customer/attach_payment_method",
            json={"customer_id": customer_id, "payment_method_ref": "pm_789"},
        )
        assert attach.status_code == 200

        record = (await client.get(f"/customer/{customer_id}")).json()
        assert record["default_payment_method_ref"] == "pm_789"
        assert record["tax_exempt"] == "REVERSE"
