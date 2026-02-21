from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any, Dict, List

from ...op.types import PHASES

if TYPE_CHECKING:
    from .core import Kernel

logger = logging.getLogger(__name__)


def build_kernelz_payload(
    kernel: "Kernel", app: Any
) -> Dict[str, Dict[str, List[str]]]:
    from ...system.diagnostics.utils import (
        label_callable as _label_callable,
        label_hook as _label_hook,
        model_iter as _model_iter,
        opspecs as _opspecs,
    )

    start = time.monotonic()
    out: Dict[str, Dict[str, List[str]]] = {}
    for model in _model_iter(app):
        kernel.get_specs(model)
        model_name = getattr(model, "__name__", "Model")
        model_map: Dict[str, List[str]] = {}
        for sp in _opspecs(model):
            seq: List[str] = []

            secdeps = [
                _label_callable(dep) if callable(dep) else str(dep)
                for dep in (getattr(sp, "secdeps", []) or [])
            ]
            deps = [
                _label_callable(dep) if callable(dep) else str(dep)
                for dep in (getattr(sp, "deps", []) or [])
            ]
            seq.extend(f"PRE_TX:secdep:{label}" for label in secdeps)
            seq.extend(f"PRE_TX:dep:{label}" for label in deps)

            chains = kernel.build(model, sp.alias)
            persist = getattr(sp, "persist", "default") != "skip"
            for phase in PHASES:
                if phase == "START_TX" and persist:
                    seq.append("START_TX:hook:sys:txn:begin@START_TX")

                for step in chains.get(phase, []) or []:
                    label = getattr(step, "__tigrbl_label", None)
                    seq.append(
                        f"{phase}:{label}"
                        if isinstance(label, str)
                        else f"{phase}:{_label_hook(step, phase)}"
                    )

                if phase == "END_TX" and persist:
                    seq.append("END_TX:hook:sys:txn:commit@END_TX")

            seen, dedup = set(), []
            for label in seq:
                if ":hook:wire:" in label:
                    if label in seen:
                        continue
                    seen.add(label)
                dedup.append(label)

            model_map[sp.alias] = dedup

        if model_map:
            out[model_name] = model_map
    duration = time.monotonic() - start
    logger.debug("kernel: built kernelz payload for app %s in %.3fs", app, duration)
    return out
