from __future__ import annotations
from typing import Any, Dict, List, Tuple

from tigrbl.table import Base
from tigrbl.specs import ColumnSpec, F, IO, S, vcol
from tigrbl.types import (
    Mapped, String, Integer, JSONB, SAEnum, PgUUID, UUID, TZDateTime)

class VwARRCustomer(Base):
    """Annual Recurring Revenue per customer (read-only view)."""
    __tablename__ = "vw_arr_customer"
    __allow_unmapped__ = True

    customer_id: Mapped[UUID] = vcol(ColumnSpec(storage=None, field=F(py_type=UUID), io=IO(out_verbs=("read","list"))))
    month: Mapped[object] = vcol(ColumnSpec(storage=None, field=F(py_type=object), io=IO(out_verbs=("read","list"))))
    arr_cents: Mapped[int] = vcol(ColumnSpec(storage=None, field=F(py_type=int), io=IO(out_verbs=("read","list"))))

    @classmethod
    def sql(cls) -> str:
        return """
        WITH mrr AS (
          SELECT
            i.customer_id AS customer_id,
            DATE_TRUNC('month', i.created_at) AS month,
            SUM(CASE WHEN COALESCE(il.proration, false) = false THEN il.amount ELSE 0 END) AS mrr_cents
          FROM invoices i
          JOIN invoice_line_items il ON il.invoice_id = i.id
          WHERE i.status = ANY(%(statuses)s)
            AND DATE_TRUNC('month', i.created_at) = DATE_TRUNC('month', COALESCE(%(asof)s, NOW()))
          GROUP BY 1, 2
        )
        SELECT
          m.customer_id,
          m.month,
          (m.mrr_cents * 12) AS arr_cents
        FROM mrr m
        WHERE (%(customer_id)s IS NULL OR m.customer_id = %(customer_id)s)
        ORDER BY m.month, m.customer_id
        """

    @classmethod
    def fetch(cls, engine_ctx, *, customer_id: str | None = None, asof: Any | None = None, include_statuses: Tuple[str, ...] = ("paid","open")) -> List[Dict[str, Any]]:
        params = {
            "customer_id": customer_id,
            "asof": asof,
            "statuses": list(include_statuses),
        }
        with engine_ctx.ro_cursor() as cur:
            cur.execute(cls.sql(), params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
