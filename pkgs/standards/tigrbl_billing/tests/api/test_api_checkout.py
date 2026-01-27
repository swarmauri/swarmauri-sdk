import pytest

from tigrbl_billing.api import api_checkout


@pytest.mark.asyncio
async def test_create_checkout_session_and_retrieve(uvicorn_client):
    async with uvicorn_client(api_checkout.app) as client:
        create = await client.post(
            "/checkout_session",
            json={"external_id": "cs_test_123", "status": "open"},
        )
        assert create.status_code == 200
        session_id = create.json()["data"]["id"]

        read = await client.get(f"/checkout_session/{session_id}")
        session = read.json()
        assert session["external_id"] == "cs_test_123"
        assert session["status"] == "open"
