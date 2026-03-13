from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    cast,
)

from .binding_spec import TransportBindingSpec

from .._spec.hook_spec import HookSpec as OpHook

from .serde import SerdeMixin
from tigrbl_atoms import StepFn

PersistPolicy = Literal["default", "prepend", "append", "override", "skip"]
Arity = Literal["collection", "member"]
TargetOp = Literal[
    "create",
    "read",
    "update",
    "replace",
    "merge",
    "delete",
    "list",
    "clear",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
    "bulk_delete",
    "custom",
]


if TYPE_CHECKING:  # pragma: no cover
    from .._spec.engine_spec import EngineCfg
    from .._spec.response_spec import ResponseSpec
    from .schema_spec import SchemaArg
else:
    EngineCfg = Any


@dataclass(frozen=True, slots=True)
class OpSpec(SerdeMixin):
    """
    Single source of truth for an operation.

    • `target` = canonical verb ("create"…,"custom")
    • `arity`  = REST shape ("member"|"collection")

    Serialization mode is inferred **only** from schema presence:
      - if model.schemas.<alias>.out exists → serialize
      - otherwise → raw pass-through

    Optional engine binding:
      - `engine` allows per-op routing (DSN string or structured mapping).
        When present, it participates in resolver precedence (op > table > router > app).
    """

    # Identity & exposure
    alias: str
    target: TargetOp
    table: Optional[type] = None
    expose_routes: bool = True
    expose_rpc: bool = True
    expose_method: bool = True
    bindings: Tuple[TransportBindingSpec, ...] = field(default_factory=tuple)

    # Optional per-op engine binding (DSN string or mapping spec)
    engine: Optional[EngineCfg] = None

    # HTTP behavior
    arity: Arity = "collection"
    http_methods: Optional[Tuple[str, ...]] = None
    path_suffix: Optional[str] = None
    tags: Tuple[str, ...] = field(default_factory=tuple)
    status_code: Optional[int] = None
    response: Optional["ResponseSpec"] = None

    # Persistence
    persist: PersistPolicy = "default"

    # Schema overrides (resolved later by binder)
    request_model: Optional[SchemaArg] = None
    response_model: Optional[SchemaArg] = None

    # Return shaping: "raw" passthrough vs "model" serialization
    returns: Literal["raw", "model"] = "raw"

    # Handler & hooks
    handler: Optional[StepFn] = None
    hooks: Tuple[OpHook, ...] = field(default_factory=tuple)

    # Diagnostics
    core: Optional[StepFn] = None
    core_raw: Optional[StepFn] = None
    extra: Mapping[str, Any] = field(default_factory=dict)
    deps: Tuple[StepFn | str, ...] = field(default_factory=tuple)
    secdeps: Tuple[StepFn | str, ...] = field(default_factory=tuple)

    @staticmethod
    def apply_alias(verb: str, alias_map: Mapping[str, str]) -> str:
        """Resolve canonical verb → alias (falls back to verb)."""

        return alias_map.get(verb, verb)

    @classmethod
    def collect(cls, table: type) -> tuple["OpSpec", ...]:
        """Collect decorated operations declared across ``table`` MRO."""

        from tigrbl_canon.mapping.op_mro_collect import mro_collect_decorated_ops

        return tuple(mro_collect_decorated_ops(table))


_ALIAS_RE = __import__("re").compile(r"^[a-z][a-z0-9_]*$")


def _ensure_spec_table(spec: Any, table: type) -> OpSpec:
    from dataclasses import replace

    if getattr(spec, "table", None) is table:
        return spec
    return replace(spec, table=table)


def _as_specs(value: Any, table: type) -> List["OpSpec"]:
    """Normalize various `__tigrbl_ops__` shapes to a list of OpSpec."""

    specs: List[OpSpec] = []
    if value is None:
        return specs

    def _from_kwargs(kwargs: Mapping[str, Any]) -> Optional[OpSpec]:
        if "alias" not in kwargs or "target" not in kwargs:
            return None
        try:
            spec = OpSpec(table=table, hooks=(), extra={}, **kwargs)
            return spec
        except Exception:  # pragma: no cover
            return None

    if isinstance(value, OpSpec) or (
        hasattr(value, "alias") and hasattr(value, "target")
    ):
        specs.append(_ensure_spec_table(value, table))
    elif isinstance(value, Mapping):
        for alias, cfg in value.items():
            if isinstance(cfg, Mapping):
                spec = _from_kwargs({"alias": alias, **cfg})
                if spec:
                    specs.append(spec)
    elif isinstance(value, Iterable):
        for item in value:
            if isinstance(item, OpSpec) or (
                hasattr(item, "alias") and hasattr(item, "target")
            ):
                specs.append(_ensure_spec_table(item, table))
            elif isinstance(item, Mapping):
                spec = _from_kwargs(item)
                if spec:
                    specs.append(spec)
    else:
        spec = _from_kwargs(
            {
                "alias": getattr(value, "alias", None),
                "target": getattr(value, "target", None),
            }
        )
        if spec:
            specs.append(spec)
    return specs


def _generate_canonical(table: type) -> List["OpSpec"]:
    from tigrbl.op.canonical import should_wire_canonical

    specs: List[OpSpec] = []
    targets: List[Tuple[str, TargetOp]] = [
        ("create", "create"),
        ("read", "read"),
        ("update", "update"),
        ("replace", "replace"),
        ("merge", "merge"),
        ("delete", "delete"),
        ("list", "list"),
        ("clear", "clear"),
        ("bulk_create", "bulk_create"),
        ("bulk_update", "bulk_update"),
        ("bulk_replace", "bulk_replace"),
        ("bulk_merge", "bulk_merge"),
        ("bulk_delete", "bulk_delete"),
    ]
    collection_targets = {
        "create",
        "list",
        "clear",
        "bulk_create",
        "bulk_update",
        "bulk_replace",
        "bulk_merge",
        "bulk_delete",
    }
    for alias, target in targets:
        if not should_wire_canonical(table, target):
            continue
        specs.append(
            OpSpec(
                table=table,
                alias=alias,
                target=target,
                arity="collection" if target in collection_targets else "member",
                persist="default",
                handler=None,
                request_model=None,
                response_model=None,
                hooks=(),
                status_code=None,
                extra={},
            )
        )
    return specs


def _collect_class_declared(model: type) -> List["OpSpec"]:
    from tigrbl.config.constants import TIGRBL_OPS_ATTR

    out: List[OpSpec] = []
    raw = getattr(model, TIGRBL_OPS_ATTR, None)
    if isinstance(raw, Mapping) or isinstance(raw, Iterable):
        out.extend(_as_specs(raw, model))
    return out


def _collect_registry(model: type) -> List["OpSpec"]:
    try:
        from tigrbl.op.model_registry import get_registered_ops
    except Exception:  # pragma: no cover
        return []

    return list(cast(Sequence[OpSpec], get_registered_ops(model)))


def _dedupe(
    existing: Dict[Tuple[str, str], "OpSpec"], incoming: Iterable["OpSpec"]
) -> None:
    for sp in incoming:
        if not hasattr(sp, "alias") or not hasattr(sp, "target"):
            continue
        if not sp.alias or not sp.target:
            continue
        existing[(sp.alias, sp.target)] = sp


def _apply_alias_ctx_to_canon(specs: List["OpSpec"], model: type) -> List["OpSpec"]:
    import logging
    from dataclasses import replace
    from tigrbl_canon.mapping.op_mro_collect import mro_alias_map_for

    logger = logging.getLogger("uvicorn")
    aliases = mro_alias_map_for(model)
    overrides: Mapping[str, Mapping[str, Any]] = (
        getattr(model, "__tigrbl_alias_overrides__", {}) or {}
    )

    if not aliases and not overrides:
        return specs

    out: List[OpSpec] = []
    for sp in specs:
        canon = sp.target
        new_alias = aliases.get(canon, sp.alias)
        mutated = sp
        if new_alias != sp.alias:
            if not isinstance(new_alias, str) or not _ALIAS_RE.match(new_alias):
                logger.warning(
                    "Invalid alias %r for verb %r on %s; keeping %r",
                    new_alias,
                    sp.target,
                    model.__name__,
                    sp.alias,
                )
            else:
                mutated = replace(mutated, alias=new_alias, path_suffix="")

        ov = overrides.get(canon)
        if ov:
            kwargs: Dict[str, Any] = {}
            if "request_schema" in ov:
                kwargs["request_model"] = ov["request_schema"]
            if "response_schema" in ov:
                kwargs["response_model"] = ov["response_schema"]
            if "persist" in ov:
                kwargs["persist"] = ov["persist"]
            if "arity" in ov:
                kwargs["arity"] = ov["arity"]
            if "rest" in ov:
                kwargs["expose_routes"] = bool(ov["rest"])
            if "engine" in ov:
                kwargs["engine"] = ov["engine"]
            if kwargs:
                mutated = replace(mutated, **kwargs)
        out.append(mutated)
    return out


def resolve(model: type) -> List["OpSpec"]:
    canon = _generate_canonical(model)
    canon = _apply_alias_ctx_to_canon(canon, model)

    class_specs = _collect_class_declared(model)
    reg_specs = _collect_registry(model)

    merged: Dict[Tuple[str, str], OpSpec] = {}
    _dedupe(merged, canon)
    _dedupe(merged, class_specs)
    _dedupe(merged, reg_specs)

    specs = list(merged.values())
    return [_ensure_spec_table(sp, model) for sp in specs]
