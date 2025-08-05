# upsertable.py
"""
Mixin that gives any SQLAlchemy model **automatic UPSERT behaviour**
for AutoAPI routers.

───────────────────────────────────────────────────────────────────────
Usage
-----

    from autoapi.v2.hooks import Phase          # for custom hooks, if needed
    from upsertable   import Upsertable
    from tables.base  import Base               # your declarative base

    class Invoice(Upsertable, Base):
        __tablename__ = "invoices"

        id         = mapped_column(Integer, primary_key=True)
        tenant_id  = mapped_column(Integer, index=True)
        number     = mapped_column(String,  unique=True)
        amount     = mapped_column(Numeric)

        # Treat (tenant_id, number) as the natural key when deciding
        # whether to INSERT or UPDATE:
        __upsert_keys__ = ("tenant_id", "number")

Add the model to one *or more* `AutoAPI` instances:

    api_public = AutoAPI(base=Base, include={Invoice}, ...)
    api_admin  = AutoAPI(base=Base, include={Invoice}, ...)

Each router receives **its own** set of hooks; no global proxy is used.
───────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from sqlalchemy import inspect

from autoapi.v2.hooks import Phase
from autoapi.v2.types import Session, HookProvider


class Upsertable(HookProvider):
    """
    Inherit from this mixin to make *create*, *update* and *replace*
    work as an **UPSERT** trio for the encompassing AutoAPI router.

    The mixin registers three `Phase.PRE_TX_BEGIN` hooks *per AutoAPI
    instance* that includes the model — eliminating global-state
    pitfalls when an app mounts multiple routers.
    """

    #: Override to specify a composite natural key.  By default the model’s
    #: primary-key column(s) are used.
    __upsert_keys__: Sequence[str] | None = None

    # ─── AutoAPI callback -------------------------------------------------
    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        """Called automatically by AutoAPI._crud(cls)."""
        model = cls.__tablename__

        for op in ("create", "update", "replace"):
            api.register_hook(Phase.PRE_TX_BEGIN, model=model, op=op)(
                cls._make_hook(op)
            )

    # ─── hook factory -----------------------------------------------------
    @classmethod
    def _make_hook(cls, verb: str):
        """
        Returns an async hook function bound to *verb*.
        The hook mutates ``ctx["env"].method`` so AutoAPI re-routes
        the operation without any client-side change.
        """

        tab = "".join(w.title() for w in cls.__tablename__.split("_"))

        async def _hook(ctx: Mapping[str, Any]) -> None:  # noqa: D401
            p: dict = ctx["payload"]  # request body
            db: Session = ctx["db"]  # current Tx

            keys = cls.__upsert_keys__ or [col.name for col in inspect(cls).primary_key]

            exists = cls._row_exists(p, db, keys)

            # Decide target verb and rewrite:
            if verb == "create" and exists:
                ctx["env"].method = f"{tab}.update"

            elif verb == "update" and not exists:
                ctx["env"].method = f"{tab}.create"

            elif verb == "replace":
                ctx["env"].method = f"{tab}.update" if exists else f"{tab}.create"

            # Otherwise keep original verb (normal path)

        return _hook

    # ─── helpers ----------------------------------------------------------
    @classmethod
    def _row_exists(
        cls, p: Mapping[str, Any], db: Session, keys: Sequence[str]
    ) -> bool:
        """
        Quick existence test on the *natural key*.
        """
        q = db.query(cls)
        for k in keys:
            q = q.filter(getattr(cls, k) == p[k])
        return db.query(q.exists()).scalar()  # type: ignore
