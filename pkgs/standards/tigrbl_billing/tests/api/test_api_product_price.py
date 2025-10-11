import pytest

from tigrbl_billing.api import api_product_price


@pytest.mark.asyncio
async def test_create_product_and_price(uvicorn_client):
    async with uvicorn_client(api_product_price.app) as client:
        product = await client.post(
            "/product",
            json={
                "stripe_product_id": "prod_123",
                "name": "Starter",
                "description": "entry",
            },
        )
        assert product.status_code == 200
        product_id = product.json()["data"]["id"]

        price = await client.post(
            "/price",
            json={"stripe_price_id": "price_123", "unit_amount": 999},
        )
        assert price.status_code == 200

        created = (await client.get(f"/product/{product_id}")).json()
        assert created["stripe_product_id"] == "prod_123"
        assert created["name"] == "Starter"
