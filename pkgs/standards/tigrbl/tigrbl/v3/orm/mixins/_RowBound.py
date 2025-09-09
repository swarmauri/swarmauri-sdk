# tigrbl/v3/mixins/_RowBound.py
from __future__ import annotations

from typing import Any, Mapping, Sequence

from ...runtime.errors import HTTP_ERROR_MESSAGES, create_standardized_error


class _RowBound:
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
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        cls._install_rowbound_hooks()

    @classmethod
    def _install_rowbound_hooks(cls) -> None:
        # Skip abstract helpers or unmapped mix-ins
        if cls.is_visible is _RowBound.is_visible:
            return
        if not hasattr(cls, "__table__"):
            return

        hook = cls._make_row_visibility_hook()
        hooks_attr = getattr(cls, "__tigrbl_hooks__", {})
        hooks = {**hooks_attr} if isinstance(hooks_attr, dict) else {}

        def _append(alias: str, phase: str, fn) -> None:
            phase_map = hooks.get(alias) or {}
            lst = list(phase_map.get(phase) or [])
            if fn not in lst:
                lst.append(fn)
            phase_map[phase] = tuple(lst)
            hooks[alias] = phase_map

        for op in ("read", "list"):
            _append(op, "POST_HANDLER", hook)

        setattr(cls, "__tigrbl_hooks__", hooks)

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
