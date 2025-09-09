# tigrbl/v2/mixins/bound.py
from __future__ import annotations

from typing import Any, Mapping, Sequence

from tigrbl.v2.hooks import Phase
from tigrbl.v2.types import HookProvider
from tigrbl.v2.jsonrpc_models import HTTP_ERROR_MESSAGES, create_standardized_error


class _RowBound(HookProvider):
    """
    Base mix-in for row-level visibility.

    Concrete subclasses **must** override:

        @staticmethod
        def is_visible(obj, ctx) -> bool

    Hooks are wired only if the subclass actually provides an implementation.
    """

    # ────────────────────────────────────────────────────────────────────
    # Tigrbl bootstrap
    # -------------------------------------------------------------------
    @classmethod
    def __tigrbl_register_hooks__(cls, api) -> None:
        # Skip abstract helpers or unmapped mix-ins
        if cls.is_visible is _RowBound.is_visible:
            return
        if not hasattr(cls, "__table__"):  # not a mapped class
            return

        for op in ("read", "list"):
            api.register_hook(model=cls, phase=Phase.POST_HANDLER, op=op)(
                cls._make_row_visibility_hook()
            )

    # ────────────────────────────────────────────────────────────────────
    # Per-request hook
    # -------------------------------------------------------------------
    @classmethod
    def _make_row_visibility_hook(cls):
        def _row_visibility_hook(ctx: Mapping[str, Any]) -> None:
            if "result" not in ctx:  # nothing to filter
                return

            res = ctx["result"]

            # LIST → keep only visible rows
            if isinstance(res, Sequence):
                ctx["result"] = [row for row in res if cls.is_visible(row, ctx)]
                return

            # READ → invisible row → pretend 404
            if not cls.is_visible(res, ctx):
                http_exc, _, _ = create_standardized_error(
                    404, message=HTTP_ERROR_MESSAGES[404]
                )
                raise http_exc

        return _row_visibility_hook

    # -------------------------------------------------------------------
    # Must be overridden
    # -------------------------------------------------------------------
    @staticmethod
    def is_visible(obj, ctx) -> bool:  # pragma: no cover
        raise NotImplementedError
