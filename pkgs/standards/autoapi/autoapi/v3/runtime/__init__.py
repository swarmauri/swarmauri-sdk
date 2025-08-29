# autoapi/v3/runtime/__init__.py
from .executor import _invoke, _Ctx
from .kernel import Kernel, build_phase_chains, run
from . import events, errors, context

# Exposed constants for diagnostics and validation
STEP_KINDS = ("secdep", "dep", "sys", "atom", "hook")
DOMAINS = ("emit", "out", "refresh", "resolve", "schema", "storage", "wire")

__all__ = [
    "_invoke",
    "_Ctx",
    "Kernel",
    "build_phase_chains",
    "run",
    "events",
    "errors",
    "context",
    "STEP_KINDS",
    "DOMAINS",
]
