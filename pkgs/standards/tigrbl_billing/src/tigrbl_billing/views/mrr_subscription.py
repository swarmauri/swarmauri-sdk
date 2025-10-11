from __future__ import annotations
from typing import Any, Dict, List, Tuple

from tigrbl.table import Base
from tigrbl.specs import ColumnSpec, F, IO, S, vcol
from tigrbl.types import (
    Mapped, String, Integer, JSONB, SAEnum, PgUUID, UUID, TZDateTime)

class VwMRRSubscription(Base):
    """Monthly Recurring Revenue per subscription (read-only view).

    Output shape: subscription_id, month, mrr_cents
    """
    __tablename__ = "vw_mrr_subscription"
    __allow_unmapped__ = True  # virtual/view columns

    subscription_id: Mapped[UUID] = vcol(
        ColumnSpec(storage=None, field=F(py_type=UUID), io=IO(out_verbs=("read","list")))
    )
    month: Mapped[object] = vcol(
        ColumnSpec(storage=None, field=F(py_type=object), io=IO(out_verbs=("read","list")))
    )
    mrr_cents: Mapped[int] = vcol(
        ColumnSpec(storage=None, field=F(py_type=int), io=IO(out_verbs=("read","list")))
    )

    @classmethod
    def sql(cls) -> str:
        return """
        WITH base AS (
          SELECT
            i.subscription_id AS subscription_id,
            DATE_TRUNC('month', i.created_at) AS month,
            SUM(CASE WHEN COALESCE(il.proration, false) = false THEN il.amount ELSE 0 END) AS mrr_cents
          FROM invoices i
          JOIN invoice_line_items il ON il.invoice_id = i.id
          WHERE i.status = ANY(%(statuses)s)
            AND DATE_TRUNC('month', i.created_at) = DATE_TRUNC('month', COALESCE(%(asof)s, NOW()))
            AND i.subscription_id IS NOT NULL
          GROUP BY 1, 2
        )
        SELECT b.subscription_id, b.month, b.mrr_cents
        FROM base b
        WHERE (%(subscription_id)s IS NULL OR b.subscription_id = %(subscription_id)s)
        ORDER BY b.month, b.subscription_id
        """

    @classmethod
    def fetch(cls, engine_ctx, *, subscription_id: str | None = None, asof: Any | None = None, include_statuses: Tuple[str, ...] = ("paid","open")) -> List[Dict[str, Any]]:
        params = {
            "subscription_id": subscription_id,
            "asof": asof,
            "statuses": list(include_statuses),
        }
        with engine_ctx.ro_cursor() as cur:
            cur.execute(cls.sql(), params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
