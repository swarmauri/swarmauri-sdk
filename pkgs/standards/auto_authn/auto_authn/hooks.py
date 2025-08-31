# auto_authn/hooks.py  (inside the AuthN package)

import logging

log = logging.getLogger(__name__)


def register_inject_hook(api):
    from autoapi.v3 import PHASE

    phase = PHASE.PRE_TX_BEGIN

    @api.register_hook(phase)
    async def _authn_inject_principal(ctx):
        p = getattr(ctx["request"].state, "principal", None)
        log.info("anon authn hook principal")
        if not p:
            return  # nothing to inject

        injected = ctx.setdefault("__autoapi_injected_fields__", {})

        def _lookup(obj, *names):
            for name in names:
                if hasattr(obj, "get"):
                    val = obj.get(name)
                    if val is not None:
                        return val
                val = getattr(obj, name, None)
                if val is not None:
                    return val
            return None

        tid = _lookup(p, "tid", "tenant_id")
        sub = _lookup(p, "sub", "user_id")
        if tid is not None:
            injected["tenant_id"] = tid
        if sub is not None:
            injected["user_id"] = sub

        log.info(
            "authn hook principal=%s", getattr(ctx["request"].state, "principal", None)
        )
        log.info(
            "authn hook injected before=%s", ctx.get("__autoapi_injected_fields__")
        )


__all__ = ["register_inject_hook", "log"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
