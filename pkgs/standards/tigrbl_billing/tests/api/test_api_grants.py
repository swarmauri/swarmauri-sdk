import pytest

from tigrbl_billing.api import api_grants


@pytest.mark.asyncio
async def test_apply_and_revoke_grant_flow(uvicorn_client):
    async with uvicorn_client(api_grants.app) as client:
        created = await client.post(
            "/credit_grant",
            json={"status": "PENDING", "revoke_amount": 0, "revoke_reason": None},
        )
        grant_id = created.json()["data"]["id"]

        apply_resp = await client.post(
            "/credit_grant/apply_grant", json={"grant_id": grant_id}
        )
        assert apply_resp.status_code == 200

        revoke_resp = await client.post(
            "/credit_grant/revoke_grant",
            json={"grant_id": grant_id, "amount": 50, "reason": "expired"},
        )
        assert revoke_resp.status_code == 200

        record = (await client.get("/credit_grant")).json()["items"][0]
        assert record["status"] == "REVOKED"
        assert record["revoke_amount"] == 50
        assert record["revoke_reason"] == "expired"
