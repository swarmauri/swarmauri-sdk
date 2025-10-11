import pytest

from tigrbl_billing.api import api_seats


@pytest.mark.asyncio
async def test_assign_and_release_seat(uvicorn_client):
    async with uvicorn_client(api_seats.app) as client:
        assign = await client.post(
            "/seat_allocation/assign",
            json={
                "subscription_item_id": "si_1",
                "subject_ref": "user-1",
                "role": "admin",
            },
        )
        assert assign.status_code == 200
        seat_id = assign.json()["data"]["id"]

        release = await client.post(
            "/seat_allocation/release", json={"seat_allocation_id": seat_id}
        )
        assert release.status_code == 200

        seat = (await client.get(f"/seat_allocation/{seat_id}")).json()
        assert seat["state"] == "RELEASED"
