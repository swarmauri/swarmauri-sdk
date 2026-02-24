import json

import pytest

from tigrbl_billing.ops import webhook_ops
from tigrbl_billing.tables.stripe_event_log import EventProcessStatus, StripeEventLog


def test_ingest_webhook_event_persists_payload():
    payload = {"id": "evt_1", "type": "invoice.created", "api_version": "2020-08-27"}

    result = webhook_ops.ingest_webhook_event(
        op_ctx=None,
        engine_ctx=None,
        schema_ctx=None,
        payload=payload,
        stripe_request_id="req_1",
    )

    assert result["status"] == EventProcessStatus.RECEIVED.value
    stored = StripeEventLog._storage[0]
    assert stored.external_id == "evt_1"
    assert stored.payload == payload
    assert stored.event_type == "invoice.created"
    assert stored.stripe_request_id == "req_1"


def test_ingest_webhook_event_is_idempotent():
    payload = {"id": "evt_2", "type": "invoice.finalized"}
    webhook_ops.ingest_webhook_event(
        op_ctx=None, engine_ctx=None, schema_ctx=None, payload=payload
    )

    result = webhook_ops.ingest_webhook_event(
        op_ctx=None,
        engine_ctx=None,
        schema_ctx=None,
        payload=json.dumps(payload),
        event_type="invoice.finalized",
    )

    assert result["status"] == EventProcessStatus.RECEIVED.value
    assert len(StripeEventLog._storage) == 1


def test_ingest_webhook_event_requires_identifier():
    with pytest.raises(ValueError):
        webhook_ops.ingest_webhook_event(
            op_ctx=None,
            engine_ctx=None,
            schema_ctx=None,
            payload={"type": "missing.id"},
        )
