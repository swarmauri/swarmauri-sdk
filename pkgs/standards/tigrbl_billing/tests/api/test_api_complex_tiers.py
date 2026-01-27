import pytest

from tigrbl_billing.api import api_complex_tiers


@pytest.mark.asyncio
async def test_create_feature_and_entitlement(uvicorn_client):
    async with uvicorn_client(api_complex_tiers.app) as client:
        feature_resp = await client.post(
            "/feature",
            json={
                "feature_key": "analytics",
                "name": "Analytics",
                "description": "Usage",
            },
        )
        assert feature_resp.status_code == 200
        feature_id = feature_resp.json()["data"]["id"]

        entitlement = await client.post(
            "/price_feature_entitlement",
            json={
                "price_id": "price-pro",
                "feature_id": feature_id,
                "entitlement": "full",
            },
        )
        assert entitlement.status_code == 200

        listing = await client.get("/price_feature_entitlement")
        entitlements = listing.json()["items"]
        assert entitlements[0]["feature_id"] == feature_id
        assert entitlements[0]["entitlement"] == "full"
