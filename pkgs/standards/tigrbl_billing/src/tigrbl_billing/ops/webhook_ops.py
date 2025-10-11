"""Webhook ingest – verifies (externally), logs, and routes. This module **only** persists the event log and returns a receipt; routing is left to your app layer to avoid tight coupling here."""

from __future__ import annotations
import json
from typing import Optional
from tigrbl_billing.tables.stripe_event_log import StripeEventLog, EventProcessStatus
from contextlib import contextmanager
from typing import Any, Tuple
from tigrbl.types import Session


def _acquire(model, op_ctx) -> Tuple[Session, Any]:
    alias = getattr(op_ctx, "alias", None) if op_ctx is not None else None
    db, release = model.acquire(op_alias=alias)
    return (db, release)


@contextmanager
def _session_for(model, op_ctx):
    db, release = _acquire(model, op_ctx)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        release()


def ingest_webhook_event(
    op_ctx,
    engine_ctx,
    schema_ctx,
    *,
    payload: dict | str,
    signature: Optional[str] = None,
    endpoint_secret: Optional[str] = None,
    account: Optional[str] = None,
    stripe_request_id: Optional[str] = None,
    api_version: Optional[str] = None,
    event_type: Optional[str] = None,
    event_created_ts: Optional[object] = None,
) -> dict:
    """
    Persist an event in `stripe_event_logs` (idempotent by external id).
    Signature verification is assumed to be performed upstream.
    `payload` may be a dict or a JSON string. If `event_type` or `api_version` are not provided, they are extracted from the payload.
    """
    if isinstance(payload, str):
        data = json.loads(payload)
    else:
        data = payload
    stripe_event_id = data.get("id")
    if not stripe_event_id:
        raise ValueError("missing stripe event id in payload")
    et = event_type or data.get("type") or "unknown"
    av = api_version or data.get("api_version")
    with _session_for(StripeEventLog, op_ctx) as db:
        obj = None
        if hasattr(db, "query"):
            obj = (
                db.query(StripeEventLog)
                .filter(StripeEventLog.external_id == stripe_event_id)
                .one_or_none()
            )
        if obj is None:
            obj = StripeEventLog(
                external_id=stripe_event_id,
                event_type=et,
                api_version=av,
                event_created_ts=event_created_ts,
                account=account,
                payload=data,
                status=EventProcessStatus.RECEIVED,
                processed_at=None,
                error_message=None,
                stripe_request_id=stripe_request_id,
            )
        else:
            pass
        db.add(obj)
        db.flush()
        return {"stripe_event_log_id": str(obj.id), "status": obj.status.value}
