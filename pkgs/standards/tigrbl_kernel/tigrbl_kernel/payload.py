from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import events as _ev
from .labels import label_hook


def _callable_label(fn: Any) -> str:
    module = getattr(fn, "__module__", "") or ""
    qualname = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    return f"{module}.{qualname}" if module else qualname


if TYPE_CHECKING:
    from .core import Kernel


def _table_iter(app: Any):
    tables = getattr(app, "tables", None)
    if isinstance(tables, dict):
        return tuple(v for v in tables.values() if isinstance(v, type))
    return ()


def _opspecs(model: type):
    return getattr(getattr(model, "opspecs", object()), "all", ()) or ()


def build_kernelz_payload(kernel: "Kernel", app: Any):
    payload: dict[str, dict[str, list[str]]] = {}
    for model in _table_iter(app):
        mname = getattr(model, "__name__", str(model))
        payload[mname] = {}
        for sp in _opspecs(model):
            labels: list[str] = []
            for dep in getattr(sp, "secdeps", ()) or ():
                labels.append(
                    f"PRE_TX_BEGIN:hook:dep:security:{_callable_label(getattr(dep, 'dependency', dep))}"
                )
            for dep in getattr(sp, "deps", ()) or ():
                labels.append(
                    f"PRE_TX_BEGIN:hook:dep:extra:{_callable_label(getattr(dep, 'dependency', dep))}"
                )

            persist = getattr(sp, "persist", "default") != "skip"
            if persist:
                labels.append("START_TX:hook:sys:txn:begin@START_TX")

            chains = kernel._build(model, sp.alias)
            for phase in _ev.PHASES:
                if phase in {"START_TX", "END_TX", "PRE_TX_BEGIN", "POST_RESPONSE"}:
                    continue
                for step in chains.get(phase, ()) or ():
                    labels.append(f"{phase}:{label_hook(step, phase)}")

            if persist:
                labels.append("END_TX:hook:sys:txn:commit@END_TX")

            for step in chains.get("POST_RESPONSE", ()) or ():
                labels.append(f"POST_RESPONSE:{label_hook(step, 'POST_RESPONSE')}")

            payload[mname][sp.alias] = labels
    return payload
