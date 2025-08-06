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

        prm = ctx["env"].params  # Pydantic model OR raw dict
        for fld, val in (("tenant_id", p["tid"]), ("owner_id", p["sub"])):
            if hasattr(prm, "__pydantic_fields__"):
                if fld in prm.model_fields and getattr(prm, fld, None) in (None, val):
                    setattr(prm, fld, val)
            elif isinstance(prm, dict):
                prm.setdefault(fld, val)


__all__ = ["register_inject_hook"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
