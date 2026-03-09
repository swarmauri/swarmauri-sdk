from __future__ import annotations

import re
from types import SimpleNamespace
from typing import Any, Mapping, Sequence

from tigrbl_runtime.hook_types import StepFn

from . import events as _ev
from .models import CompiledPhase
from .types import (
    DEFAULT_PHASE_ORDER,
    EFFECT_BY_ATOM_NAME,
    EFFECT_NONE,
    EGRESS_PHASES,
    LOWER_KIND_ASYNC_DIRECT,
    LOWER_KIND_SPLIT_EXTRACTABLE,
    LOWER_KIND_SYNC_EXTRACTABLE,
    ROUTE_SPINE_ATOMS,
)


def _table_iter(app: Any) -> Sequence[Any]:
    tables = getattr(app, "tables", None)
    if isinstance(tables, dict):
        return tuple(v for v in tables.values() if isinstance(v, type))
    if isinstance(tables, Sequence) and not isinstance(tables, (str, bytes, bytearray)):
        return tuple(tables)
    return ()


def _opspecs(model: Any) -> Sequence[Any]:
    ops = getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ()) or ()
    if ops:
        return tuple(ops)

    table_ops = getattr(model, "ops", ()) or ()
    if table_ops:
        return tuple(table_ops)

    declared_ops = getattr(model, "__tigrbl_ops__", ()) or ()
    if declared_ops:
        return tuple(declared_ops)

    return ()


def _canonicalize_app(app: Any) -> Any:
    try:
        from tigrbl_canon.mapping.spec_normalization import normalize_app_spec
        from tigrbl_core._spec.app_spec import AppSpec
    except Exception:
        return app

    if isinstance(app, AppSpec):
        return normalize_app_spec(app)
    return app


def _label_callable(fn: Any) -> str:
    name = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    module = getattr(fn, "__module__", None)
    return f"{module}.{name}" if module else name


def _atom_name(step: Any) -> str | None:
    for attr in ("__tigrbl_atom_name__", "__tigrbl_name__", "name"):
        value = getattr(step, attr, None)
        if isinstance(value, str) and value:
            return value
    label = getattr(step, "__tigrbl_label", None)
    if isinstance(label, str) and label:
        prefix = label.split("@", 1)[0]
        if ":hook:wire:" in prefix:
            prefix = prefix.split(":hook:wire:", 1)[1]
        prefix = prefix.replace(":", ".")
        if prefix:
            return prefix
    return None


def _label_step(step: Any, phase: str) -> str:
    label = getattr(step, "__tigrbl_label", None)
    if isinstance(label, str) and "@" in label:
        return label
    module = getattr(step, "__module__", "") or ""
    name = getattr(step, "__name__", "") or ""
    if (
        module.startswith("tigrbl_ops_oltp.crud")
        or module.startswith("tigrbl_core.core.crud")
        and name
    ):
        return f"hook:wire:tigrbl:core:crud:ops:{name}@{phase}"
    atom_name = _atom_name(step)
    if isinstance(atom_name, str) and atom_name:
        return f"hook:wire:{atom_name.replace('.', ':')}@{phase}"
    return f"hook:wire:{_label_callable(step).replace('.', ':')}@{phase}"


def _classify_step_lowering(step: Any, phase: str) -> str:
    name = _atom_name(step)
    if name in ROUTE_SPINE_ATOMS:
        return LOWER_KIND_SYNC_EXTRACTABLE
    if name in {"ingress.method_extract", "ingress.path_extract"}:
        return LOWER_KIND_SYNC_EXTRACTABLE
    if name in {
        "route.params_normalize",
        "route.payload_select",
        "route.rpc_envelope_parse",
        "ingress.headers_parse",
        "ingress.query_parse",
    }:
        return LOWER_KIND_SPLIT_EXTRACTABLE
    if phase in EGRESS_PHASES:
        return LOWER_KIND_ASYNC_DIRECT
    return LOWER_KIND_ASYNC_DIRECT


def _effect_descriptor_for_step(step: Any) -> tuple[int, tuple[int, ...]]:
    name = _atom_name(step)
    if not isinstance(name, str) or not name:
        return EFFECT_NONE, ()
    effect_id = EFFECT_BY_ATOM_NAME.get(name, EFFECT_NONE)
    return int(effect_id), ()


def _compile_path_pattern(path: str) -> tuple[re.Pattern[str], tuple[str, ...]]:
    names: list[str] = []

    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        names.append(name)
        return rf"(?P<{name}>[^/]+)"

    pattern = "^" + re.sub(r"\{([^{}]+)\}", _replace, path) + "$"
    return re.compile(pattern), tuple(names)


def _route_payload_template() -> dict[str, Any]:
    return {
        "http.rest": {"exact": {}, "templated": []},
        "https.rest": {"exact": {}, "templated": []},
        "http.jsonrpc": {},
        "https.jsonrpc": {},
        "ws": {"exact": {}, "templated": []},
        "wss": {"exact": {}, "templated": []},
    }


def _phase_info_map(
    phase_order: tuple[str, ...] = DEFAULT_PHASE_ORDER,
) -> tuple[dict[str, CompiledPhase], tuple[str, ...], tuple[str, ...]]:
    phases: dict[str, CompiledPhase] = {}
    if hasattr(_ev, "PHASES"):
        for name in phase_order:
            try:
                is_error = bool(getattr(_ev, "is_error_phase", lambda _n: False)(name))
            except Exception:
                is_error = False
            in_tx = name in {
                "START_TX",
                "PRE_HANDLER",
                "HANDLER",
                "END_TX",
                "POST_COMMIT",
            }
            phases[name] = CompiledPhase(
                name=name,
                stage_in=None,
                stage_out=None,
                in_tx=in_tx,
                is_error=is_error,
            )
    mainline = tuple(
        name
        for name in phase_order
        if not phases.get(name, CompiledPhase(name, None, None)).is_error
    )
    error = tuple(
        name
        for name in phase_order
        if phases.get(name, CompiledPhase(name, None, None)).is_error
    )
    return phases, mainline, error


def deepmerge_phase_chains(
    *phase_maps: Mapping[str, Sequence[StepFn]],
) -> dict[str, list[StepFn]]:
    merged: dict[str, list[StepFn]] = {}
    for phase_map in phase_maps:
        for phase, steps in (phase_map or {}).items():
            merged.setdefault(phase, []).extend(list(steps or ()))
    return {phase: list(steps) for phase, steps in merged.items()}
