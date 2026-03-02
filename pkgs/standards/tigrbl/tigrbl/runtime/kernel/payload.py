from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from .. import events as _ev
from ..labels import label_callable, label_hook

if TYPE_CHECKING:
    from .core import Kernel


def build_kernelz_payload(kernel: "Kernel", app: Any):
    payload: dict[str, dict[str, list[str]]] = {}
    tables = getattr(app, "tables", {})
    if isinstance(tables, Mapping):
        models = list(tables.values())
    else:
        models = list(tables or ())

    for model in models:
        model_name = getattr(model, "__name__", str(model))
        model_payload: dict[str, list[str]] = {}
        for spec in getattr(getattr(model, "opspecs", None), "all", ()) or ():
            alias = getattr(spec, "alias", None)
            if not isinstance(alias, str):
                continue

            labels: list[str] = []
            secdeps = tuple(getattr(spec, "secdeps", ()) or ())
            deps = tuple(getattr(spec, "deps", ()) or ())
            for dep in secdeps:
                dep_fn = getattr(dep, "dependency", dep)
                labels.append(
                    f"PRE_TX_BEGIN:hook:dep:security:{label_callable(dep_fn)}"
                )
            for dep in deps:
                dep_fn = getattr(dep, "dependency", dep)
                labels.append(f"PRE_TX_BEGIN:hook:dep:extra:{label_callable(dep_fn)}")

            persist_mode = getattr(spec, "persist", "default")
            if persist_mode != "skip":
                labels.append("START_TX:hook:sys:txn:begin@START_TX")

            chains = kernel.build(model, alias)
            for phase in _ev.PHASES:
                if phase in {
                    "INGRESS_BEGIN",
                    "INGRESS_PARSE",
                    "INGRESS_ROUTE",
                    "EGRESS_SHAPE",
                    "EGRESS_FINALIZE",
                    "START_TX",
                    "END_TX",
                }:
                    continue
                if phase == "POST_RESPONSE" and persist_mode != "skip":
                    labels.append("END_TX:hook:sys:txn:commit@END_TX")
                for step in chains.get(phase, ()) or ():
                    labels.append(f"{phase}:{label_hook(step, phase)}")

            if persist_mode != "skip" and "POST_RESPONSE" not in chains:
                labels.append("END_TX:hook:sys:txn:commit@END_TX")

            model_payload[alias] = labels
        payload[model_name] = model_payload

    return payload
