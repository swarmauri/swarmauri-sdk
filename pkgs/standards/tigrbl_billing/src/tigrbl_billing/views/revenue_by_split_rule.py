from __future__ import annotations
from typing import Any, Dict, List, Tuple

from tigrbl.table import Base
from tigrbl.specs import ColumnSpec, F, IO, S, vcol
from tigrbl.types import (
    Mapped, String, Integer, JSONB, SAEnum, PgUUID, UUID, TZDateTime)

class VwRevenueBySplitRule(Base):
    """Platform take-rate vs partner payouts, grouped by split rule key (read-only)."""
    __tablename__ = "vw_revenue_by_split_rule"
    __allow_unmapped__ = True

    split_rule_key: Mapped[str] = vcol(ColumnSpec(storage=None, field=F(py_type=str), io=IO(out_verbs=("read","list"))))
    gross_amount_cents: Mapped[int] = vcol(ColumnSpec(storage=None, field=F(py_type=int), io=IO(out_verbs=("read","list"))))
    platform_fee_cents: Mapped[int] = vcol(ColumnSpec(storage=None, field=F(py_type=int), io=IO(out_verbs=("read","list"))))
    partner_payout_cents: Mapped[int] = vcol(ColumnSpec(storage=None, field=F(py_type=int), io=IO(out_verbs=("read","list"))))
    platform_take_rate_pct: Mapped[object] = vcol(ColumnSpec(storage=None, field=F(py_type=object), io=IO(out_verbs=("read","list"))))

    @classmethod
    def sql(cls) -> str:
        return """
        WITH base AS (
          SELECT
            COALESCE((pi.metadata ->> 'split_rule_key'), 'unknown') AS split_rule_key,
            pi.id AS pi_id,
            pi.amount AS gross_amount
          FROM payment_intents pi
          WHERE pi.status = ANY(%(pi_statuses)s)
            AND (%(date_from)s IS NULL OR pi.created_at >= %(date_from)s)
            AND (%(date_to)s   IS NULL OR pi.created_at <  %(date_to)s)
        ),
        fees AS (
          SELECT
            af.originating_payment_intent_id AS pi_id,
            SUM(af.amount) AS platform_fee
          FROM application_fees af
          GROUP BY 1
        ),
        payouts AS (
          SELECT
            t.source_payment_intent_id AS pi_id,
            SUM(t.amount) AS partner_payout
          FROM transfers t
          GROUP BY 1
        )
        SELECT
          b.split_rule_key,
          SUM(b.gross_amount) AS gross_amount_cents,
          COALESCE(SUM(f.platform_fee), 0) AS platform_fee_cents,
          COALESCE(SUM(p.partner_payout), 0) AS partner_payout_cents,
          CASE WHEN SUM(b.gross_amount) > 0
               THEN ROUND((COALESCE(SUM(f.platform_fee),0)::numeric / SUM(b.gross_amount)::numeric) * 100, 2)
               ELSE 0 END AS platform_take_rate_pct
        FROM base b
        LEFT JOIN fees f ON f.pi_id = b.pi_id
        LEFT JOIN payouts p ON p.pi_id = b.pi_id
        GROUP BY b.split_rule_key
        ORDER BY gross_amount_cents DESC, b.split_rule_key
        """

    @classmethod
    def fetch(cls, engine_ctx, *, date_from: Any | None = None, date_to: Any | None = None, pi_statuses: Tuple[str, ...] = ("succeeded","processing","requires_capture")) -> List[Dict[str, Any]]:
        params = {
            "date_from": date_from,
            "date_to": date_to,
            "pi_statuses": list(pi_statuses),
        }
        with engine_ctx.ro_cursor() as cur:
            cur.execute(cls.sql(), params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
