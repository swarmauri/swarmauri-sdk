import pytest

from tigrbl_billing.api import api_banded_pricing


@pytest.mark.asyncio
async def test_create_price_tier_and_list(uvicorn_client):
    async with uvicorn_client(api_banded_pricing.app) as client:
        create = await client.post(
            "/price_tier",
            json={"price_id": "price-std", "up_to": 100, "unit_amount": 2500},
        )
        assert create.status_code == 200
        tier_id = create.json()["data"]["id"]

        listing = await client.get("/price_tier")
        tiers = listing.json()["items"]
        assert any(tier["id"] == tier_id for tier in tiers)
        assert tiers[0]["unit_amount"] == 2500
