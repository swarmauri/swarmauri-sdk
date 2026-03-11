from tigrbl.decorators.hook import *  # noqa: F401,F403
from tigrbl.decorators.hook import HOOK_DECLS_ATTR
from tigrbl_concrete._concrete import Hook

__all__ = list(globals().get("__all__", ())) + ["HOOK_DECLS_ATTR", "Hook"]
