# auto_authn/hooks.py  (inside the AuthN package)


def register_inject_hook(api):
    from autoapi.v2.hooks import Phase

    allow_anon = api._allow_anon

    @api.hook(Phase.PRE_TX_BEGIN)  # PRE‑DB, works for CRUD & RPC
    async def _inject(ctx):
        if getattr(ctx.get("env"), "method", None) in allow_anon:
            return
        p = ctx["request"].state.principal
        if not p:
            return

        ctx["is_admin"] = p.get("is_admin", False)

        injected = ctx.setdefault("__autoapi_injected_fields__", {})
        tid = p.get("tid")
        sub = p.get("sub")
        if tid is not None:
            injected["tenant_id"] = tid
        if sub is not None:
            injected["user_id"] = sub
            injected["owner_id"] = sub


__all__ = ["register_inject_hook"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
