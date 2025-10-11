from __future__ import annotations
from typing import Any, Dict, List, Tuple

from tigrbl.table import Base
from tigrbl.specs import ColumnSpec, F, IO, S, vcol
from tigrbl.types import (
    Mapped, String, Integer, JSONB, SAEnum, PgUUID, UUID, TZDateTime)

class VwARPUMonthly(Base):
    """Average Revenue Per User (customer) by month (read-only)."""
    __tablename__ = "vw_arpu_monthly"
    __allow_unmapped__ = True

    month: Mapped[object] = vcol(ColumnSpec(storage=None, field=F(py_type=object), io=IO(out_verbs=("read","list"))))
    revenue_cents: Mapped[int] = vcol(ColumnSpec(storage=None, field=F(py_type=int), io=IO(out_verbs=("read","list"))))
    paying_customers: Mapped[int] = vcol(ColumnSpec(storage=None, field=F(py_type=int), io=IO(out_verbs=("read","list"))))
    arpu_cents: Mapped[int] = vcol(ColumnSpec(storage=None, field=F(py_type=int), io=IO(out_verbs=("read","list"))))

    @classmethod
    def sql(cls) -> str:
        return """
        SELECT
          DATE_TRUNC('month', i.created_at) AS month,
          SUM(i.amount_paid) AS revenue_cents,
          COUNT(DISTINCT i.customer_id) AS paying_customers,
          CASE WHEN COUNT(DISTINCT i.customer_id) = 0 THEN 0
               ELSE (SUM(i.amount_paid) / COUNT(DISTINCT i.customer_id)) END AS arpu_cents
        FROM invoices i
        WHERE i.status = 'paid'
          AND (%(date_from)s IS NULL OR i.created_at >= %(date_from)s)
          AND (%(date_to)s   IS NULL OR i.created_at <  %(date_to)s)
        GROUP BY 1
        ORDER BY 1
        """

    @classmethod
    def fetch(cls, engine_ctx, *, date_from: Any | None = None, date_to: Any | None = None) -> List[Dict[str, Any]]:
        params = {"date_from": date_from, "date_to": date_to}
        with engine_ctx.ro_cursor() as cur:
            cur.execute(cls.sql(), params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
