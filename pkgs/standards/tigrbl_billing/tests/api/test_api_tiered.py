import pytest

from tigrbl_billing.api import api_tiered


@pytest.mark.asyncio
async def test_create_price_and_tier_relationship(uvicorn_client):
    async with uvicorn_client(api_tiered.app) as client:
        price = await client.post(
            "/price",
            json={"stripe_price_id": "price-tiered", "unit_amount": 1999},
        )
        price_id = price.json()["data"]["id"]

        tier = await client.post(
            "/price_tier",
            json={"price_id": price_id, "up_to": 5, "unit_amount": 1500},
        )
        assert tier.status_code == 200

        tiers = (await client.get("/price_tier")).json()["items"]
        assert tiers[0]["price_id"] == price_id
        assert tiers[0]["unit_amount"] == 1500
