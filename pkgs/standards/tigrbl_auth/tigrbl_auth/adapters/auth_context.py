from __future__ import annotations

from tigrbl_auth.deps import Request, TIGRBL_AUTH_CONTEXT_ATTR


def set_auth_context(request: Request, principal: dict | None) -> None:
    """Populate request.state with the auth context expected by Tigrbl.

    Parameters
    ----------
    request:
        Incoming FastAPI request whose state should be populated.
    principal:
        Principal dictionary containing ``tenant_id`` (``tid``) and ``user_id``
        (``sub``). May be ``None`` when no authenticated principal is present.
    """
    ctx: dict[str, str] = {}
    if principal:
        tid = principal.get("tid") or principal.get("tenant_id")
        uid = principal.get("sub") or principal.get("user_id")
        if tid is not None:
            ctx["tenant_id"] = tid
        if uid is not None:
            ctx["user_id"] = uid
    setattr(request.state, TIGRBL_AUTH_CONTEXT_ATTR, ctx)


__all__ = ["set_auth_context"]
