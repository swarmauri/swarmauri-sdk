# auto_authn/hooks.py  (inside the AuthN package)


def register_inject_hook(api):
    from autoapi.v2.hooks import Phase
    from secrets import token_urlsafe
    from .orm.tables import ApiKey

    @api.hook(Phase.PRE_TX_BEGIN)  # PRE‑DB, works for CRUD & RPC
    async def _inject(ctx):
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

    @api.hook(Phase.PRE_TX_BEGIN, model="ApiKey", op="create")
    async def _generate_key(ctx):
        prm = ctx["env"].params
        if hasattr(prm, "__pydantic_fields__"):
            if getattr(prm, "raw_key", None):
                raise ValueError("raw_key cannot be provided")
            prm.digest = ApiKey.digest_of(raw := token_urlsafe(8))
        elif isinstance(prm, dict):
            if prm.get("raw_key"):
                raise ValueError("raw_key cannot be provided")
            raw = token_urlsafe(8)
            prm["digest"] = ApiKey.digest_of(raw)
        else:
            raw = token_urlsafe(8)
        ctx["raw_api_key"] = raw

    @api.hook(Phase.POST_RESPONSE, model="ApiKey", op="create")
    async def _inject_key(ctx):
        raw = ctx.get("raw_api_key")
        if not raw:
            return
        result = dict(ctx.get("result", {}))
        result["api_key"] = raw
        ctx["result"] = result


__all__ = ["register_inject_hook"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
