# tigrbl/v2/model_facets.py
from __future__ import annotations
from types import SimpleNamespace
from typing import Callable, Dict, List, Type

from .crud_builder import create_crud_operations
from .rpc_adapter import _wrap_rpc
from .schema import _schema
from .op_wiring import collect_all_specs_for_table
from ..ops.spec import OpSpec
from ..types.op_config_provider import should_wire_canonical

# Canonical verbs in order (arity inferred later)
_CANON = (
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
    "clear",
)


class _OpSpecRegistry:
    """Per-model registry with on_change callback that re-syncs namespaces."""

    def __init__(self, table: Type, on_change: Callable[[], None]) -> None:
        self.table = table
        self._specs: List[OpSpec] = []
        self._on_change = on_change

    def set(self, specs: List[OpSpec]) -> None:
        self._specs = list(specs)
        self._on_change()

    def add(self, *specs: OpSpec) -> None:
        self._specs.extend(specs)
        self._on_change()

    def remove(self, pred: Callable[[OpSpec], bool]) -> None:
        self._specs = [s for s in self._specs if not pred(s)]
        self._on_change()

    def all(self) -> List[OpSpec]:
        return list(self._specs)


def _canonical_specs_with_cores(
    model: Type,
) -> tuple[Dict[str, OpSpec], Dict[str, Callable], Dict[str, Callable]]:
    """Build canonical specs + core/raw handlers once from CRUD builder."""
    pk_name = next(iter(model.__table__.primary_key.columns)).name
    crud = create_crud_operations(model, pk_name)
    spec_map: Dict[str, OpSpec] = {}
    handlers: Dict[str, Callable] = {}
    raw_handlers: Dict[str, Callable] = {}

    # Map canonical verbs → IN/OUT schemas and core callables
    wire = {
        "create": (
            crud["schemas"]["create"],
            crud["schemas"]["read_out"],
            crud["create"],
        ),
        "read": (crud["schemas"]["read_in"], crud["schemas"]["read_out"], crud["read"]),
        "update": (
            crud["schemas"]["update"],
            crud["schemas"]["read_out"],
            crud["update"],
        ),
        "replace": (
            crud["schemas"]["create"],
            crud["schemas"]["read_out"],
            crud["update"],
        ),
        "delete": (crud["schemas"]["delete_in"], None, crud["delete"]),
        "list": (crud["schemas"]["list"], crud["schemas"]["read_out"], crud["list"]),
        "clear": (None, None, crud["clear"]),
        # bulk_* are built by routes_builder today; leave as pass-through unless wired by OpSpec
    }

    for verb in _CANON:
        if not should_wire_canonical(model, verb):
            continue
        IN, OUT, core = wire.get(verb, (None, None, None))
        if core is None:
            continue
        spec_map[verb] = OpSpec(
            alias=verb,
            target=verb,
            table=model,
            expose_routes=True,
            expose_rpc=True,
            expose_method=True,
        )
        raw_handlers[verb] = core
        # normalized handler via rpc adapter (pydantic in/out + overlay)
        pk = pk_name
        rpc = _wrap_rpc(core, (IN or dict), (OUT or dict), pk, model)
        handlers[verb] = rpc
    return spec_map, handlers, raw_handlers


def init_model_facets(model: Type) -> None:
    """One-time class bootstrap; safe to call from Base.__init_subclass__."""
    ns = SimpleNamespace()
    ns.columns = {c.key: c for c in model.__table__.columns}
    ns.config = SimpleNamespace(
        defaults_mode=getattr(model, "__tigrbl_defaults_mode__", "all"),
        defaults_include=getattr(model, "__tigrbl_defaults_include__", set()),
        defaults_exclude=getattr(model, "__tigrbl_defaults_exclude__", set()),
        verb_aliases=dict((getattr(model, "__tigrbl_verb_aliases__", {}) or {})),
        verb_alias_policy=getattr(model, "__tigrbl_verb_alias_policy__", "both"),
        nested_paths=getattr(model, "__tigrbl_nested_paths__", None),
    )
    ns.schemas = SimpleNamespace(inp={}, out={})
    ns.rpc = SimpleNamespace()  # CamelCase names, like API.rpc ids
    ns.handlers = SimpleNamespace()  # normalized (pydantic in/out)
    ns.raw_handlers = SimpleNamespace()  # raw core callables
    ns.hooks: Dict[str, list] = {}  # optional: per-verb hook buckets

    # Canonical cores + handlers
    canon_specs, canon_handlers, canon_raw = _canonical_specs_with_cores(model)

    # Fill schemas for canon verbs
    for v, h in canon_handlers.items():
        # Recreate the IN/OUT models to expose on the class for introspection
        if v in ("clear",):
            continue
        if v == "read":
            IN = _schema(
                model,
                verb="delete",
                include={next(iter(model.__table__.primary_key.columns)).name},
                name=f"{model.__name__}ReadIn",
            )
            OUT = _schema(model, verb="read")
        elif v == "delete":
            IN = _schema(
                model,
                verb="delete",
                include={next(iter(model.__table__.primary_key.columns)).name},
            )
            OUT = None
        elif v == "list":
            IN = _schema(model, verb="list")
            OUT = _schema(model, verb="read")
        elif v in ("create", "replace"):
            IN = _schema(model, verb="create")
            OUT = _schema(model, verb="read")
        elif v == "update":
            IN = _schema(
                model,
                verb="update",
                exclude={next(iter(model.__table__.primary_key.columns)).name},
            )
            OUT = _schema(model, verb="read")
        else:
            IN = OUT = None
        if IN:
            ns.schemas.inp[v] = IN
        if OUT:
            ns.schemas.out[v] = OUT

    # Attach canonical handlers
    for v, f in canon_handlers.items():
        setattr(ns.handlers, v, f)
    for v, f in canon_raw.items():
        setattr(ns.raw_handlers, v, f)

    # OpSpec registry: class-declared + decorators + imperative registry
    def _sync_from_specs():
        # Start from computed canonical specs
        active = dict(canon_specs)
        # Merge decorated/custom/registered specs (impl/op_wiring already knows how to collect)
        for s in collect_all_specs_for_table(model):
            active[(s.alias if s.target == "custom" else s.alias)] = s

        # Expose per-OpSpec handlers/rpc if custom/alias
        for spec_key, spec in list(active.items()):
            alias = spec.alias
            # Custom handler? expose raw + normalized + rpc
            if spec.target == "custom" and spec.handler:
                # raw: table method receives (table, *, ctx, db, request, payload)
                async def _raw(payload, db, _h=spec.handler, _t=model):
                    return await _h(_t, ctx={}, db=db, request=None, payload=payload)

                setattr(ns.raw_handlers, alias, _raw)

                IN = spec.request_model or dict
                OUT = spec.response_model or dict
                pk = next(iter(model.__table__.primary_key.columns)).name
                setattr(ns.handlers, alias, _wrap_rpc(_raw, IN, OUT, pk, model))

            # CamelCase rpc id
            camel = "".join(w.title() for w in alias.split("_"))

            def _rpc(payload, db, _alias=alias, _m=model):
                # Exact same callable that API.rpc will hold
                return getattr(_m.handlers, _alias)(payload, db)

            setattr(ns.rpc, camel, _rpc)

    ns.op_registry = _OpSpecRegistry(model, on_change=_sync_from_specs)
    ns.router_factory = None  # filled by routes_builder bridge (below)
    _sync_from_specs()

    # Publish on the class
    model.opspecs = ns.op_registry
    model.schemas = ns.schemas
    model.rpc = ns.rpc
    model.handlers = ns.handlers
    model.raw_handlers = ns.raw_handlers
    model.columns = ns.columns
    model.table_config = ns.config
    model.__tigrbl__ = ns  # keep a bag
