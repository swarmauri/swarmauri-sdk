from __future__ import annotations
from typing import Any, Dict, List, Tuple

from tigrbl.table import Base
from tigrbl.specs import ColumnSpec, F, IO, vcol
from tigrbl.types import (
    Mapped,
)


class VwCohortRetention(Base):
    """Cohort retention snapshot by subscription start month (read-only)."""

    __tablename__ = "vw_cohort_retention"
    __allow_unmapped__ = True

    cohort_month: Mapped[object] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=object), io=IO(out_verbs=("read", "list"))
        )
    )
    cohort_size: Mapped[int] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=int), io=IO(out_verbs=("read", "list"))
        )
    )
    active_now: Mapped[int] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=int), io=IO(out_verbs=("read", "list"))
        )
    )
    retention_rate_now_pct: Mapped[object] = vcol(
        ColumnSpec(
            storage=None, field=F(py_type=object), io=IO(out_verbs=("read", "list"))
        )
    )

    @classmethod
    def sql(cls) -> str:
        return """
        WITH cohorts AS (
          SELECT
            DATE_TRUNC('month', s.start_date) AS cohort_month,
            s.status AS status
          FROM subscriptions s
          WHERE (%(asof)s IS NULL OR s.created_at <= %(asof)s)
        )
        SELECT
          cohort_month,
          COUNT(*) AS cohort_size,
          SUM(CASE WHEN status = ANY(%(activeish)s) THEN 1 ELSE 0 END) AS active_now,
          ROUND( (SUM(CASE WHEN status = ANY(%(activeish)s) THEN 1 ELSE 0 END)::numeric
                / NULLIF(COUNT(*),0)::numeric) * 100, 2) AS retention_rate_now_pct
        FROM cohorts
        GROUP BY cohort_month
        ORDER BY cohort_month
        """

    @classmethod
    def fetch(
        cls,
        engine_ctx,
        *,
        asof: Any | None = None,
        activeish: Tuple[str, ...] = (
            "incomplete",
            "trialing",
            "active",
            "past_due",
            "unpaid",
        ),
    ) -> List[Dict[str, Any]]:
        params = {
            "asof": asof,
            "activeish": list(activeish),
        }
        with engine_ctx.ro_cursor() as cur:
            cur.execute(cls.sql(), params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
