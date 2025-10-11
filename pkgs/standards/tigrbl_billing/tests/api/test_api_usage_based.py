import pytest

from tigrbl_billing.api import api_usage_based


@pytest.mark.asyncio
async def test_rollup_periodic_sums_usage(uvicorn_client):
    async with uvicorn_client(api_usage_based.app) as client:
        for quantity, ts in [(3, 1), (5, 2), (7, 5)]:
            await client.post(
                "/usage_event",
                json={
                    "subscription_item_id": "si-rollup",
                    "usage_event_id": f"evt-{ts}",
                    "quantity": quantity,
                    "event_ts": ts,
                    "feature_key": "jobs",
                    "customer_id": "cust-usage",
                    "currency": "usd",
                },
            )

        rollup = await client.post(
            "/usage_rollup/rollup_periodic",
            json={
                "subscription_item_id": "si-rollup",
                "period_start": 0,
                "period_end": 10,
            },
        )
        body = rollup.json()
        assert rollup.status_code == 200
        assert body["quantity_sum"] == 15
