from __future__ import annotations

from dataclasses import dataclass, field
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Tuple,
)

from .binding_spec import TransportBindingSpec

from .._spec.hook_spec import HookSpec as OpHook

from .serde import SerdeMixin
from .hook_types import StepFn
from .op_utils import _maybe_await, _normalize_persist, _unwrap

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
        """Collect resolved operations for ``table`` (canonical + declared + registry)."""
        return tuple(resolve(table))


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
    from tigrbl_core.op.canonical import should_wire_canonical

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
    from tigrbl_core.config.constants import TIGRBL_OPS_ATTR

    out: List[OpSpec] = []
    raw = getattr(model, TIGRBL_OPS_ATTR, None)
    if isinstance(raw, Mapping) or isinstance(raw, Iterable):
        out.extend(_as_specs(raw, model))
    return out


def _collect_registry(model: type) -> List["OpSpec"]:
    """Core spec resolution is intentionally package-local.

    Runtime registry integrations belong in concrete/runtime layers.
    """

    return []


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

    logger = logging.getLogger("uvicorn")
    aliases = _mro_alias_map_for(model)
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


def _ensure_ctx(
    *, request: Any = None, db: Any = None, seed: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    ctx: Dict[str, Any] = dict(seed or {})
    if request is not None:
        ctx.setdefault("request", request)
    if db is not None:
        ctx.setdefault("db", db)
    return ctx


def _merge_mro_dict(model: type, attr: str) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for base in reversed(model.__mro__):
        merged.update(getattr(base, attr, {}) or {})
    return merged


def _mro_alias_map_for(table: type) -> Dict[str, str]:
    return _merge_mro_dict(table, "__tigrbl_aliases__")


def _wrap_ctx_core(table: type, func: Any) -> StepFn:
    async def core(p=None, *, db=None, request=None, ctx: Dict[str, Any] | None = None):
        ctx = _ensure_ctx(request=request, db=db, seed=ctx)
        if p is not None:
            ctx["payload"] = p
        bound = func.__get__(table, table)
        sig = inspect.signature(bound)
        kwargs: Dict[str, Any] = {}
        args: list[Any] = []
        if "ctx" in sig.parameters:
            kwargs["ctx"] = ctx
        elif "_ctx" in sig.parameters:
            kwargs["_ctx"] = ctx
        if "obj" in sig.parameters:
            kwargs["obj"] = ctx.get("obj")
        elif "_obj" in sig.parameters:
            kwargs["_obj"] = ctx.get("obj")
        if "objs" in sig.parameters:
            kwargs["objs"] = ctx.get("objs")
        elif "_objs" in sig.parameters:
            kwargs["_objs"] = ctx.get("objs")
        if "id" in sig.parameters:
            kwargs["id"] = ctx.get("ident")
        elif "_id" in sig.parameters:
            kwargs["_id"] = ctx.get("ident")

        if not kwargs:
            positional = [
                param
                for param in sig.parameters.values()
                if param.kind
                in {
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                }
                and param.default is inspect._empty
            ]
            if len(positional) == 1:
                args.append(ctx)

        res = await _maybe_await(bound(*args, **kwargs))
        return res if res is not None else ctx.get("result")

    core.__name__ = getattr(func, "__name__", "core")
    core.__qualname__ = getattr(func, "__qualname__", core.__name__)
    core.__tigrbl_ctx_wrapper__ = True
    return core


def _mro_collect_decorated_ops(table: type) -> List["OpSpec"]:
    out: List[OpSpec] = []
    seen: set[str] = set()

    for base in table.__mro__:
        for name, attr in vars(base).items():
            if name in seen:
                continue
            func = _unwrap(attr)
            op_spec: OpSpec | None = getattr(func, "__tigrbl_op_spec__", None)
            if op_spec is None:
                op_spec = getattr(func, "__tigrbl_op_decl__", None)
            if op_spec is None:
                continue

            resolved_alias = op_spec.alias or op_spec.target or name
            out.append(
                OpSpec(
                    table=table,
                    alias=resolved_alias,
                    target=op_spec.target,
                    arity=op_spec.arity,
                    persist=_normalize_persist(op_spec.persist),
                    handler=_wrap_ctx_core(table, func),
                    http_methods=getattr(op_spec, "http_methods", None),
                    path_suffix=getattr(op_spec, "path_suffix", ""),
                    tags=tuple(getattr(op_spec, "tags", ()) or ()),
                    request_model=getattr(op_spec, "request_model", None),
                    response_model=getattr(op_spec, "response_model", None),
                    hooks=tuple(getattr(op_spec, "hooks", ()) or ()),
                    status_code=getattr(op_spec, "status_code", None),
                    expose_routes=getattr(op_spec, "expose_routes", None),
                    expose_rpc=getattr(op_spec, "expose_rpc", None),
                    expose_method=getattr(op_spec, "expose_method", None),
                    engine=getattr(op_spec, "engine", None),
                    response=getattr(op_spec, "response", None),
                    returns=getattr(op_spec, "returns", None),
                    core=getattr(op_spec, "core", None),
                    core_raw=getattr(op_spec, "core_raw", None),
                    extra=dict(getattr(op_spec, "extra", {}) or {}),
                    deps=tuple(getattr(op_spec, "deps", ()) or ()),
                    secdeps=tuple(getattr(op_spec, "secdeps", ()) or ()),
                )
            )
            seen.add(name)

    return out
