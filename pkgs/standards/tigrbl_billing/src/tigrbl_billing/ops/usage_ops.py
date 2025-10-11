"""Usage ops – record events and roll up to billing windows."""

from __future__ import annotations
from tigrbl.types import UUID
from tigrbl_billing.tables.usage_event import UsageEvent
from tigrbl_billing.tables.usage_rollup import UsageRollup
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


def rollup_usage_periodic(
    op_ctx,
    engine_ctx,
    schema_ctx,
    *,
    subscription_item_id: UUID,
    period_start: object,
    period_end: object,
) -> dict:
    """Compute a simple SUM rollup for a period (DB-only; Stripe finalization happens on invoice)."""
    with _session_for(UsageRollup, op_ctx) as db:
        total = 0
        if hasattr(db, "query"):
            q = db.query(UsageEvent).filter(
                UsageEvent.subscription_item_id == subscription_item_id
            )
            q = q.filter(
                UsageEvent.event_ts >= period_start, UsageEvent.event_ts < period_end
            )
            total = sum((e.quantity for e in q.all()))
        existing = None
        if hasattr(db, "query"):
            existing = (
                db.query(UsageRollup)
                .filter(
                    UsageRollup.subscription_item_id == subscription_item_id,
                    UsageRollup.period_start == period_start,
                    UsageRollup.period_end == period_end,
                )
                .one_or_none()
            )
        if existing is None:
            r = UsageRollup(
                subscription_item_id=subscription_item_id,
                period_start=period_start,
                period_end=period_end,
                quantity_sum=total,
                last_event_ts=None,
            )
        else:
            r = existing
            r.quantity_sum = total
        db.add(r)
        db.flush()
        return {"usage_rollup_id": str(r.id), "quantity_sum": r.quantity_sum}
