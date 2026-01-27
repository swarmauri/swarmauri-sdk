from __future__ import annotations
from typing import Any, Dict, List

from tigrbl.table import Base
from tigrbl.specs import ColumnSpec, F, IO, vcol
from tigrbl.types import (
    Mapped,
)


class VwDunningFunnel(Base):
    """Open→Paid funnel by period with counts per invoice status (read-only)."""

    __tablename__ = "vw_dunning_funnel"
    __allow_unmapped__ = True

    period: Mapped[object] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=object), io=IO(out_verbs=("read", "list"))
        )
    )
    draft: Mapped[int] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=int), io=IO(out_verbs=("read", "list"))
        )
    )
    open: Mapped[int] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=int), io=IO(out_verbs=("read", "list"))
        )
    )
    paid: Mapped[int] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=int), io=IO(out_verbs=("read", "list"))
        )
    )
    uncollectible: Mapped[int] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=int), io=IO(out_verbs=("read", "list"))
        )
    )
    void: Mapped[int] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=int), io=IO(out_verbs=("read", "list"))
        )
    )
    open_to_paid_pct: Mapped[object] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=object), io=IO(out_verbs=("read", "list"))
        )
    )

    @classmethod
    def _sql(cls, trunc: str) -> str:
        return f"""
        WITH base AS (
          SELECT
            DATE_TRUNC('{trunc}', i.created_at) AS period,
            i.status AS status
          FROM invoices i
          WHERE (%(date_from)s IS NULL OR i.created_at >= %(date_from)s)
            AND (%(date_to)s   IS NULL OR i.created_at <  %(date_to)s)
        )
        SELECT
          period,
          SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) AS draft,
          SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open,
          SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid,
          SUM(CASE WHEN status = 'uncollectible' THEN 1 ELSE 0 END) AS uncollectible,
          SUM(CASE WHEN status = 'void' THEN 1 ELSE 0 END) AS void,
          CASE WHEN SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) = 0
               THEN 0
               ELSE ROUND(
                  (SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END)::numeric
                   / NULLIF(SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END),0)::numeric) * 100, 2)
          END AS open_to_paid_pct
        FROM base
        GROUP BY period
        ORDER BY period
        """

    @classmethod
    def fetch(
        cls,
        engine_ctx,
        *,
        grain: str = "month",
        date_from: Any | None = None,
        date_to: Any | None = None,
    ) -> List[Dict[str, Any]]:
        trunc = "day" if grain == "day" else "month"
        sql = cls._sql(trunc)
        params = {"date_from": date_from, "date_to": date_to}
        with engine_ctx.ro_cursor() as cur:
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
