from types import SimpleNamespace

from tigrbl_billing.ops import usage_ops
from tigrbl_billing.tables.usage_event import UsageEvent
from tigrbl_billing.tables.usage_rollup import UsageRollup


def test_rollup_usage_periodic_creates_rollup():
    UsageEvent._storage.extend(
        [
            UsageEvent(subscription_item_id="item_1", event_ts=1, quantity=2),
            UsageEvent(subscription_item_id="item_1", event_ts=5, quantity=3),
            UsageEvent(subscription_item_id="item_1", event_ts=11, quantity=7),
        ]
    )

    result = usage_ops.rollup_usage_periodic(
        SimpleNamespace(alias="usage"),
        engine_ctx=None,
        schema_ctx=None,
        subscription_item_id="item_1",
        period_start=0,
        period_end=10,
    )

    assert result["quantity_sum"] == 5
    stored = UsageRollup._storage[0]
    assert stored.subscription_item_id == "item_1"
    assert stored.period_start == 0
    assert stored.period_end == 10
    assert stored.quantity_sum == 5


def test_rollup_usage_periodic_updates_existing_rollup():
    existing = UsageRollup(
        subscription_item_id="item_2",
        period_start=0,
        period_end=10,
        quantity_sum=1,
        last_event_ts=None,
    )
    UsageRollup._storage.append(existing)
    UsageEvent._storage.extend(
        [
            UsageEvent(subscription_item_id="item_2", event_ts=2, quantity=4),
        ]
    )

    result = usage_ops.rollup_usage_periodic(
        SimpleNamespace(alias="usage"),
        engine_ctx=None,
        schema_ctx=None,
        subscription_item_id="item_2",
        period_start=0,
        period_end=10,
    )

    assert result["quantity_sum"] == 4
    assert UsageRollup._storage[0] is existing
    assert existing.quantity_sum == 4
