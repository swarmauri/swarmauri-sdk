from __future__ import annotations
from typing import Any, Dict, List, Tuple

from tigrbl.table import Base
from tigrbl.specs import ColumnSpec, F, IO, S, vcol
from tigrbl.types import (
    Mapped, String, Integer, JSONB, SAEnum, PgUUID, UUID, TZDateTime)

class VwUsageCoverageRatio(Base):
    """Coverage = metered usage / entitlement limit per feature (read-only)."""
    __tablename__ = "vw_usage_coverage_ratio"
    __allow_unmapped__ = True

    subscription_item_id: Mapped[UUID] = vcol(ColumnSpec(storage=None, field=F(py_type=UUID), io=IO(out_verbs=("read","list"))))
    feature_id: Mapped[UUID] = vcol(ColumnSpec(storage=None, field=F(py_type=UUID), io=IO(out_verbs=("read","list"))))
    usage_qty: Mapped[int] = vcol(ColumnSpec(storage=None, field=F(py_type=int), io=IO(out_verbs=("read","list"))))
    entitlement_limit: Mapped[int | None] = vcol(ColumnSpec(storage=None, field=F(py_type=int | None), io=IO(out_verbs=("read","list"))))
    coverage_ratio: Mapped[object | None] = vcol(ColumnSpec(storage=None, field=F(py_type=object | None), io=IO(out_verbs=("read","list"))))

    @classmethod
    def sql(cls) -> str:
        return """
        WITH usage AS (
          SELECT
            ue.subscription_item_id,
            ue.feature_id,
            SUM(ue.quantity) AS usage_qty
          FROM usage_events ue
          WHERE ue.event_ts >= %(period_start)s
            AND ue.event_ts <  %(period_end)s
            AND ue.feature_id IS NOT NULL
          GROUP BY 1,2
        ),
        sitems AS (
          SELECT si.id AS subscription_item_id, si.subscription_id, si.price_id
          FROM subscription_items si
        ),
        ent AS (
          SELECT
            pfe.price_id,
            pfe.feature_id,
            pfe.limit_per_period
          FROM price_feature_entitlements pfe
        )
        SELECT
          u.subscription_item_id,
          u.feature_id,
          u.usage_qty,
          e.limit_per_period AS entitlement_limit,
          CASE
            WHEN e.limit_per_period IS NULL OR e.limit_per_period = 0 THEN NULL
            ELSE ROUND((u.usage_qty::numeric / e.limit_per_period::numeric), 4)
          END AS coverage_ratio
        FROM usage u
        JOIN sitems si ON si.subscription_item_id = u.subscription_item_id
        JOIN ent e ON e.price_id = si.price_id AND e.feature_id = u.feature_id
        WHERE (%(subscription_id)s IS NULL OR si.subscription_id = %(subscription_id)s)
        ORDER BY u.subscription_item_id, u.feature_id
        """

    @classmethod
    def fetch(cls, engine_ctx, *, period_start: Any, period_end: Any, subscription_id: str | None = None) -> List[Dict[str, Any]]:
        params = {"period_start": period_start, "period_end": period_end, "subscription_id": subscription_id}
        with engine_ctx.ro_cursor() as cur:
            cur.execute(cls.sql(), params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
