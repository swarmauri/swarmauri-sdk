# autoapi/v2/mixins/bound.py  (new file)

from __future__ import annotations
from typing import Any, Mapping, Sequence

from autoapi.v2.hooks import Phase
from autoapi.v2.types import HookProvider


class _RowBound(HookProvider):
    """
    Base class for mix-ins that want to trim *read* / *list* results
    to what the caller is allowed to see.
    Sub-classes must implement `is_visible(obj, ctx) -> bool`.
    """

    # ――― AutoAPI bootstrap ―――
    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        model = cls.__tablename__

        for op in ("read", "list"):
            api.register_hook(Phase.POST_HANDLER, model=model, op=op)(cls._make_hook())

    # ――― per-request hook ―――
    @classmethod
    def _make_hook(cls):
        async def _hook(ctx: Mapping[str, Any]) -> None:
            if "result" not in ctx:  # defensive
                return

            res = ctx["result"]
            if isinstance(res, Sequence):  # list → drop the invisible rows
                ctx["result"] = [row for row in res if cls.is_visible(row, ctx)]
            else:  # single object (read)
                if not cls.is_visible(res, ctx):
                    # mimic 404 to avoid leaking existence
                    from autoapi.v2.jsonrpc_models import create_standardized_error

                    http_exc, _, _ = create_standardized_error(404)
                    raise http_exc

        return _hook

    # sub-classes must override
    @staticmethod
    def is_visible(obj, ctx) -> bool:
        raise NotImplementedError


# ----- Examples ----------------------------------------------------
# Concrete Mixins with one-liner predicates
# class AuthnBound(_RowBound):
#     @staticmethod
#     def is_visible(obj, ctx) -> bool:
#         # example: only rows belonging to the caller’s tenant
#         return obj.tenant_id == ctx["request"].state.principal.tenant_id


# class MemberBound(_RowBound):
#     @staticmethod
#     def is_visible(obj, ctx) -> bool:
#         # example: rows for Organisations the caller is a member of
#         return obj.org_id in ctx["request"].state.memberships
