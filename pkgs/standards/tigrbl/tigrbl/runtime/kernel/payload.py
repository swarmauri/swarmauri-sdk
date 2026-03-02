from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from .. import events as _ev

if TYPE_CHECKING:
    from .core import Kernel


def _opspec_for(model: type, alias: str) -> Any | None:
    specs = getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ()) or ()
    for spec in specs:
        if getattr(spec, "alias", None) == alias:
            return spec
    return None


def _dep_name(dep: Any) -> str:
    fn = getattr(dep, "dependency", dep)
    module = getattr(fn, "__module__", "") or ""
    qn = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    return f"{module}.{qn}" if module else qn


def build_kernelz_payload(kernel: "Kernel", app: Any):
    """Build diagnostics payload from the canonical compiled kernel plan."""
    plan = kernel.compile_plan(app)
    payload: dict[str, dict[str, list[str]]] = {}

    skip_phases = {
        "INGRESS_BEGIN",
        "INGRESS_PARSE",
        "INGRESS_ROUTE",
        "EGRESS_SHAPE",
        "EGRESS_FINALIZE",
        "START_TX",
        "END_TX",
    }

    for op_index, meta in enumerate(plan.opmeta):
        table_name = getattr(meta.model, "__name__", str(meta.model))
        labels: list[str] = []

        spec = _opspec_for(meta.model, meta.alias)
        if spec is not None:
            for dep in getattr(spec, "secdeps", ()) or ():
                labels.append(f"PRE_TX_BEGIN:hook:dep:security:{_dep_name(dep)}")
            for dep in getattr(spec, "deps", ()) or ():
                labels.append(f"PRE_TX_BEGIN:hook:dep:extra:{_dep_name(dep)}")

            target = (getattr(spec, "target", meta.alias) or meta.alias).lower()
            persist = getattr(spec, "persist", "default")
            persistent = persist != "skip" and target not in {"read", "list"}
        else:
            persistent = meta.target not in {"read", "list"}

        if persistent:
            labels.append("START_TX:hook:sys:txn:begin@START_TX")

        chains = plan.phase_chains.get(op_index, {})
        for phase in _ev.PHASES:
            if phase in skip_phases or phase == "POST_RESPONSE":
                continue
            for step in chains.get(phase, ()) or ():
                label = getattr(step, "__tigrbl_label", None)
                if isinstance(label, str):
                    labels.append(f"{phase}:{label}")

        if persistent:
            labels.append("END_TX:hook:sys:txn:commit@END_TX")

        for step in chains.get("POST_RESPONSE", ()) or ():
            label = getattr(step, "__tigrbl_label", None)
            if isinstance(label, str):
                labels.append(f"POST_RESPONSE:{label}")

        payload.setdefault(table_name, {})[meta.alias] = labels

    return payload
