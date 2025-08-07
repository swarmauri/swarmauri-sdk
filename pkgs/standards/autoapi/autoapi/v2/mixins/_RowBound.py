# autoapi/v2/mixins/bound.py
from __future__ import annotations

from typing import Any, Mapping, Sequence

from autoapi.v2.hooks import Phase
from autoapi.v2.types import HookProvider
from autoapi.v2.jsonrpc_models import create_standardized_error


class _RowBound(HookProvider):
    """
    Base mix-in for row-level visibility.

    Sub-classes must implement:

        @staticmethod
        def is_visible(obj, ctx) -> bool: ...

    The mix-in registers POST-HANDLER hooks for **read** and **list** so that:
      • In *list* results, invisible rows are dropped.
      • In *read*, an invisible row is treated as a 404 (cannot leak existence).
    """

    # ────────────────────────────────────────────────────────────────────
    # AutoAPI bootstrap: register hooks once per verb
    # -------------------------------------------------------------------
    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        for op in ("read", "list"):
            api.register_hook(model=cls, phase=Phase.POST_HANDLER, op=op)(
                cls._make_hook()
            )

    # ────────────────────────────────────────────────────────────────────
    # Per-request hook factory
    # -------------------------------------------------------------------
    @classmethod
    def _make_hook(cls):
        def _hook(ctx: Mapping[str, Any]) -> None:
            # Defensive: make sure we even got a result
            if "result" not in ctx:
                return

            res = ctx["result"]

            # List → keep only visible rows
            if isinstance(res, Sequence):
                ctx["result"] = [row for row in res if cls.is_visible(row, ctx)]
                return

            # Read → treat invisible as 404
            if not cls.is_visible(res, ctx):
                http_exc, _, _ = create_standardized_error(404)
                raise http_exc

        return _hook

    # -------------------------------------------------------------------
    # Sub-classes override this.
    # -------------------------------------------------------------------
    @staticmethod
    def is_visible(obj, ctx) -> bool:  # pragma: no cover
        raise NotImplementedError
