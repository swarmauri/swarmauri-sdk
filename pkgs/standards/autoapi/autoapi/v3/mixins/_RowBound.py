# autoapi/v2/mixins/bound.py
from __future__ import annotations

from typing import Any, Mapping, Sequence

from autoapi.v2.jsonrpc_models import HTTP_ERROR_MESSAGES, create_standardized_error


class _RowBound:
    """
    Base mix-in for row-level visibility.

    Concrete subclasses **must** override:

        @staticmethod
        def is_visible(obj, ctx) -> bool

    Hooks are wired only if the subclass actually provides an implementation.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._install_row_visibility_hooks()

    @classmethod
    def _install_row_visibility_hooks(cls) -> None:
        if cls.is_visible is _RowBound.is_visible:
            return
        if not hasattr(cls, "__table__"):
            return
        hooks = getattr(cls, "__autoapi_hooks__", None) or {}
        hooks = {**hooks}
        for op in ("read", "list"):
            phase_map = hooks.get(op) or {}
            lst = list(phase_map.get("POST_HANDLER") or [])
            lst.append(cls._make_row_visibility_hook())
            phase_map["POST_HANDLER"] = tuple(lst)
            hooks[op] = phase_map
        setattr(cls, "__autoapi_hooks__", hooks)

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
