"""
autoapi/v2/routes_builder.py  –  Route building functionality for AutoAPI.

This module contains the logic for building both REST and RPC routes from
CRUD operations, including nested routing and RBAC guards.
"""

from __future__ import annotations

import functools
import inspect
import re
from types import SimpleNamespace
from typing import Annotated, Any, List, Optional

from sqlalchemy import inspect as _sa_inspect  # ← added
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..types import APIRouter, Depends, Request, Path, Body
from ..types.op_config_provider import should_wire_canonical
from ..naming import (
    alias_policy,
    canonical_name,
    public_verb,
    route_label,
    snake_to_camel,
)

from ..jsonrpc_models import _RPCReq, create_standardized_error
from ..mixins import AsyncCapable, BulkCapable, Replaceable

from .op_wiring import attach_op_specs
from .rpc_adapter import _wrap_rpc
from .schema import _schema
from ._runner import _invoke


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _attach(root: Any, resource: str, op: str, fn: Any) -> None:
    """Attach *fn* under ``root.resource.op`` creating namespaces as needed."""
    ns = getattr(root, resource, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(root, resource, ns)
    setattr(ns, op, fn)


def _strip_parent_fields(base: type, *, drop: set[str]) -> type:
    """
    Return a shallow clone of *base* with every field in *drop* removed, so that
    child schemas used by nested routes do not expose parent identifiers.
    """
    from typing import get_args, get_origin
    from pydantic import BaseModel, ConfigDict, create_model

    if not drop:
        return base

    if get_origin(base) in (list, List):  # List[Model] → List[Stripped]
        elem = get_args(base)[0]
        return list[_strip_parent_fields(elem, drop=drop)]

    if isinstance(base, type) and issubclass(base, BaseModel):
        fld_spec = {
            n: (fld.annotation, fld)
            for n, fld in base.model_fields.items()
            if n not in drop
        }
        cfg = getattr(base, "model_config", ConfigDict())
        cls = create_model(f"{base.__name__}SansParents", __config__=cfg, **fld_spec)
        cls.model_rebuild(force=True)
        return cls

    return base  # primitive / dict / etc.


def _register_routes_and_rpcs(  # noqa: N802 – bound as method
    self,
    model: type,
    tab: str,
    pk: str,
    SCreate,
    SReadOut,  # ← read OUTPUT schema
    SReadIn,  # ← read INPUT (pk-only) schema
    SDeleteIn,  # ← delete INPUT (pk-only) schema
    SUpdate,
    SListIn,
    _create,
    _read,
    _update,
    _delete,
    _list,
    _clear,
) -> None:
    """
    Build both REST and RPC surfaces for one SQLAlchemy model.

    The REST routes are thin facades: each fabricates a _RPCReq envelope and
    delegates to `_invoke`, ensuring lifecycle parity with /rpc.
    """
    print(f"_register_routes_and_rpcs model={model} tab={tab} pk={pk}")

    # ---------- sync / async detection --------------------------------
    is_async = (
        bool(self.get_async_db)
        if self.get_db is None
        else issubclass(model, AsyncCapable)
    )
    provider = self.get_async_db if is_async else self.get_db
    print(f"Async mode: {is_async}")
    # Choose a concrete DB dependency type per mode (no unions, no Optional)
    DBDep = (
        Annotated[AsyncSession, Depends(provider)]
        if is_async
        else Annotated[Session, Depends(provider)]
    )

    pk_col = next(iter(model.__table__.primary_key.columns))
    pk_type = getattr(pk_col.type, "python_type", str)

    resource = model.__name__

    # ---------- verb specification -----------------------------------
    spec: List[tuple] = [
        ("create", "POST", "", 201, SCreate, SReadOut, _create),
        ("list", "GET", "", 200, SListIn, List[SReadOut], _list),
        ("clear", "DELETE", "", 204, None, None, _clear),
        ("read", "GET", "/{item_id}", 200, SReadIn, SReadOut, _read),
        ("update", "PATCH", "/{item_id}", 200, SUpdate, SReadOut, _update),
        ("delete", "DELETE", "/{item_id}", 204, SDeleteIn, None, _delete),
    ]
    if issubclass(model, Replaceable):
        print("Model is Replaceable; adding replace spec")
        spec.append(
            (
                "replace",
                "PUT",
                "/{item_id}",
                200,
                SCreate,
                SReadOut,
                functools.partial(_update, full=True),
            )
        )
    if issubclass(model, BulkCapable):
        print("Model is BulkCapable; adding bulk specs")
        # keep REST path style aligned with current codebase ("/bulk")
        spec += [
            (
                "bulk_create",
                "POST",
                "/bulk",
                201,
                List[SCreate],
                List[SReadOut],
                _create,
            ),
            (
                "bulk_update",
                "PATCH",
                "/bulk",
                200,
                List[SUpdate],
                List[SReadOut],
                _update,
            ),
            (
                "bulk_replace",
                "PUT",
                "/bulk",
                200,
                List[SCreate],
                List[SReadOut],
                functools.partial(_update, full=True),
            ),
            ("bulk_delete", "DELETE", "/bulk", 204, List[SDeleteIn], None, _delete),
        ]

    # ─── table-level policy: include/exclude canonical verbs ─────────
    spec = [t for t in spec if should_wire_canonical(model, t[0])]

    # ---------- nested routing ---------------------------------------
    raw_pref = self._nested_prefix(model) or ""
    nested_pref = re.sub(r"/{2,}", "/", raw_pref).rstrip("/") or None
    nested_vars = re.findall(r"{(\w+)}", raw_pref)
    print(f"Nested prefix: {nested_pref} vars: {nested_vars}")

    allow_cb = getattr(model, "__autoapi_allow_anon__", None)
    if callable(allow_cb):
        _allow_verbs = set(allow_cb())
    else:
        _allow_verbs = set(allow_cb or [])
    self._allow_anon.update({canonical_name(tab, v) for v in _allow_verbs})
    if _allow_verbs:
        print(f"Anon allowed verbs: {_allow_verbs}")

    flat_router = APIRouter(prefix=f"/{tab}", tags=[resource])
    routers = (
        (flat_router,)
        if nested_pref is None
        else (flat_router, APIRouter(prefix=nested_pref, tags=[f"nested-{resource}"]))
    )

    # ---------- RBAC guard -------------------------------------------
    def _guard(scope: str):
        async def inner(request: Request):
            if self._authorize and not self._authorize(scope, request):
                print(f"Authorization failed for scope {scope}")
                http_exc, _, _ = create_standardized_error(403, rpc_code=-32095)
                raise http_exc

        return Depends(inner)

    # ---------- endpoint factory -------------------------------------
    for verb, http, path, status, In, Out, core in spec:
        m_id_canon = canonical_name(tab, verb)

        # RPC input model for adapter (distinct from REST signature)
        rpc_in = In or dict
        if verb in {"update", "replace"}:
            # For update/replace we want the verb-specific model without the PK
            # (it's supplied separately via the path parameter)
            rpc_in = _schema(model, verb=verb, exclude={pk})

        # Route label (name/summary) using alias policy
        label = route_label(
            resource, verb, alias_policy(model), public_verb(model, verb)
        )

        def _factory(
            is_nested_router, *, verb=verb, path=path, In=In, core=core, m_id=m_id_canon
        ):
            params: list[inspect.Parameter] = [
                inspect.Parameter(  # request always first
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                )
            ]

            # parent keys become path vars on nested router
            if is_nested_router:
                for nv in nested_vars:
                    params.append(
                        inspect.Parameter(
                            nv,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            annotation=Annotated[str, Path(...)],
                        )
                    )

            # primary key path var (must be a Path param, not a query)
            if "{item_id}" in path:
                params.append(
                    inspect.Parameter(
                        "item_id",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[pk_type, Path(...)],
                    )
                )

            # payload (query for list, body for create/update/replace; none for read/delete/clear)
            def _visible(t: type) -> type:
                return (
                    _strip_parent_fields(t, drop=set(nested_vars))
                    if is_nested_router
                    else t
                )

            if verb == "list":
                params.append(
                    inspect.Parameter(
                        "p",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[_visible(In), Depends()],
                    )
                )
                params.append(
                    inspect.Parameter(
                        "db",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=DBDep,
                    )
                )
            elif verb == "clear" and issubclass(model, BulkCapable) and path == "":
                # allow optional body for bulk_delete on the "/" route if you adopt unified semantics later
                params.append(
                    inspect.Parameter(
                        "db",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=DBDep,
                    )
                )
                params.append(
                    inspect.Parameter(
                        "p",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[Optional[List[SDeleteIn]], Body()],
                        default=None,
                    )
                )
            elif In is not None and verb not in ("read", "delete", "clear"):
                params.append(
                    inspect.Parameter(
                        "p",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[_visible(In), Body(embed=False)],
                    )
                )
                params.append(
                    inspect.Parameter(
                        "db",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=DBDep,
                    )
                )
            else:
                params.append(
                    inspect.Parameter(
                        "db",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=DBDep,
                    )
                )

            # ---- callable body ---------------------------------------
            async def _impl(**kw):
                print(f"Endpoint {m_id} invoked with {kw}")
                # do NOT annotate with a union here; keep it untyped
                db = kw.pop("db")
                req: Request = kw.pop("request")
                p = kw.pop("p", None)
                item_id = kw.pop("item_id", None)
                parent_kw = {k: kw[k] for k in nested_vars if k in kw}

                # assemble RPC-style param dict
                def _dump(obj):
                    if hasattr(obj, "model_dump"):
                        return obj.model_dump(exclude_unset=True, exclude_none=True)
                    return obj

                if verb in {
                    "bulk_create",
                    "bulk_update",
                    "bulk_replace",
                    "bulk_delete",
                }:
                    # p is a list of models/dicts
                    lst = []
                    for it in p or []:
                        lst.append(_dump(it))
                    rpc_params = lst
                else:
                    match verb:
                        case "read" | "delete":
                            rpc_params = {pk: item_id}
                        case "update" | "replace":
                            rpc_params = {pk: item_id, **_dump(p)}
                        case "list":
                            rpc_params = _dump(p)
                        case "clear":
                            rpc_params = {}
                        case _:
                            rpc_params = _dump(p) if p is not None else {}

                if parent_kw:
                    if isinstance(rpc_params, dict):
                        rpc_params.update(parent_kw)
                    elif isinstance(rpc_params, list):
                        rpc_params = [
                            {**parent_kw, **(e if isinstance(e, dict) else _dump(e))}
                            for e in rpc_params
                        ]

                print(f"RPC params built: {rpc_params}")
                env = _RPCReq(id=None, method=m_id, params=rpc_params)
                # Ensure a ctx dict exists and merge it into the call ctx
                if getattr(req.state, "ctx", None) is None:
                    req.state.ctx = {}
                ctx = {"request": req, "db": db, "env": env, "params": env.params}
                _ext = getattr(req.state, "ctx", None)
                if isinstance(_ext, dict):
                    ctx.update(_ext)

                def _build_args(_p):
                    match verb:
                        case (
                            "create"
                            | "bulk_create"
                            | "bulk_update"
                            | "bulk_replace"
                            | "bulk_delete"
                        ):
                            return (_p,)
                        case "list":
                            return (p,)
                        case "clear":
                            return ()
                        case "read" | "delete":
                            return (_p[pk],)
                        case "update" | "replace":
                            body = {k: v for k, v in _p.items() if k != pk}
                            return (_p[pk], body)
                        case _:
                            return ()

                if isinstance(db, AsyncSession):

                    def exec_fn(_m, _p, _db=db):
                        return _db.run_sync(lambda s: core(*_build_args(_p), s))

                    return await _invoke(
                        self, m_id, params=rpc_params, ctx=ctx, exec_fn=exec_fn
                    )

                def _direct_call(_m, _p, _db=db):
                    return core(*_build_args(_p), _db)

                result = await _invoke(
                    self, m_id, params=rpc_params, ctx=ctx, exec_fn=_direct_call
                )
                print(f"Endpoint {m_id} returning {result}")
                return result

            _impl.__name__ = f"{verb}_{tab}"
            wrapped = functools.wraps(_impl)(_impl)
            wrapped.__signature__ = inspect.Signature(parameters=params)
            return wrapped

        # Common error responses
        from ..jsonrpc_models import HTTP_ERROR_MESSAGES

        COMMON_ERRORS = {
            400: {"description": HTTP_ERROR_MESSAGES[400]},
            404: {"description": HTTP_ERROR_MESSAGES[404]},
            409: {"description": HTTP_ERROR_MESSAGES[409]},
            422: {"description": HTTP_ERROR_MESSAGES[422]},
            500: {"description": HTTP_ERROR_MESSAGES[500]},
        }

        # mount on routers
        for rtr in routers:
            deps = [_guard(m_id_canon)]
            if m_id_canon not in self._allow_anon:
                deps.insert(0, self._authn_dep)
            print(f"Mounting route {path} for verb {verb} on router {rtr}")
            rtr.add_api_route(
                path,
                _factory(rtr is not flat_router),
                methods=[http],
                status_code=status,
                response_model=None if verb == "create" else Out,
                responses=COMMON_ERRORS,
                dependencies=deps,
                name=label,  # ← route name reflects alias policy
                summary=label,  # ← docs summary ditto
            )

        # ─── register schemas on API namespace (for discovery / testing) ──
        verb_camel = snake_to_camel(verb)
        for s, suffix in ((In, "In"), (Out, "Out"), (rpc_in, "RpcIn")):
            if not isinstance(s, type) or s is dict:
                continue
            canon = f"{resource}{verb_camel}{suffix}"
            if canon not in self._schemas:
                self._schemas[canon] = s
                setattr(self.schemas, canon, s)

        # JSON-RPC shim (single callable for this canonical op)
        rpc_fn = _wrap_rpc(core, rpc_in, Out, pk, model)
        print(
            f"Registered RPC method {m_id_canon} with IN={getattr(rpc_in, '__name__', rpc_in)} OUT={getattr(Out, '__name__', Out)}"
        )
        self.rpc.add(m_id_canon, rpc_fn)

        # ── in-process convenience wrappers (canonical + alias) ────────
        def _make_runner(bound_method: str):
            def _runner(payload, *, db=None, _method=bound_method, _api=self):
                """
                Helper so you can call:  api.methods.User.create(...), etc.
                """
                if db is None:  # auto-open sync session
                    if _api.get_db is None:
                        raise TypeError(
                            "Supply a Session via db=... "
                            "or register get_db when constructing AutoAPI()"
                        )
                    gen = _api.get_db()
                    db_ = next(gen)
                    try:
                        return _api.rpc[_method](payload, db_)
                    finally:
                        try:
                            next(gen)  # finish generator → close
                        except StopIteration:
                            pass
                else:
                    return _api.rpc[_method](payload, db)

            return _runner

        # Register canonical
        camel = f"{resource}{snake_to_camel(verb)}"
        _runner_canon = _make_runner(m_id_canon)
        self._method_ids[m_id_canon] = _runner_canon
        setattr(self.core, camel, core)
        _attach(self.core, resource, verb, core)
        _attach(self.methods, resource, verb, _runner_canon)
        print(f"Registered helper method {camel}")

        # Ensure container for core_raw
        if not hasattr(self, "core_raw"):

            class _CE: ...

            self.core_raw = _CE()

        async def _core_raw(payload, *, db=None, _core=core, _verb=verb, _pk=pk):
            # Build args in the same way your RPC shim would
            def _build_args(_p):
                def _dump(o):
                    return (
                        o.model_dump(exclude_unset=True, exclude_none=True)
                        if hasattr(o, "model_dump")
                        else o
                    )

                match _verb:
                    case "create" | "list":
                        return (_p,)
                    case "bulk_create" | "bulk_update" | "bulk_replace" | "bulk_delete":
                        if isinstance(_p, list):
                            return ([_dump(x) for x in _p],)
                        return (_dump(_p),)
                    case "clear":
                        return ()
                    case "read" | "delete":
                        d = _dump(_p)
                        return (d[_pk],)
                    case "update" | "replace":
                        d = _dump(_p)
                        body = {k: v for k, v in d.items() if k != _pk}
                        return (d[_pk], body)
                return ()

            # 1) Caller supplied a DB
            if db is not None:
                if hasattr(db, "run_sync"):  # AsyncSession
                    return await db.run_sync(lambda s: _core(*_build_args(payload), s))
                # Plain Session
                return _core(*_build_args(payload), db)

            # 2) No DB supplied: auto-open a sync session only if available
            if self.get_db is None:
                raise TypeError(
                    "core_raw requires a DB (AsyncSession or Session) when get_db is not configured"
                )

            gen = self.get_db()
            s = next(gen)
            try:
                return _core(*_build_args(payload), s)
            finally:
                try:
                    next(gen)  # close
                except StopIteration:
                    pass

        setattr(self.core_raw, camel, _core_raw)
        _attach(self.core_raw, resource, verb, _core_raw)


    # ─── OpSpec-powered verbs (aliases + custom + skip/override) ────
    attach_op_specs(self, flat_router, model)
    if len(routers) > 1:
        try:
            attach_op_specs(self, routers[1], model)  # nested router
        except TypeError:
            pass

    # include routers
    self.router.include_router(flat_router)
    if len(routers) > 1:
        self.router.include_router(routers[1])

    # ─────────────────────────────────────────────────────────────────
    # Bind per-table namespaces onto the **class object** (not instances)
    # Exposes: Model.schemas / Model.methods / Model.rpc / Model.core / Model.core_raw
    # Also expose Model.router (flat/nested) and convenience aliases:
    #   Model.handlers (→ methods) and Model.raw_handlers (→ core)
    # ─────────────────────────────────────────────────────────────────
    decl = model

    # resolve what we already registered on the API object
    methods_ns  = getattr(self.methods,  resource, SimpleNamespace())
    core_ns     = getattr(self.core,     resource, SimpleNamespace())
    core_raw_ns = getattr(self.core_raw, resource, SimpleNamespace())

    # Build a schemas namespace by collecting all schema classes that start with this resource's prefix
    schemas_ns = SimpleNamespace()
    _pref = resource
    for _name, _cls in getattr(self, "_schemas", {}).items():
        if not isinstance(_cls, type) or _cls is dict:
            continue
        if not _name.startswith(_pref):
            continue
        short = _name[len(_pref):]  # "CreateIn", "UpdateOut", "ReadRpcIn", ...
        if short and short[0].isupper():
            setattr(schemas_ns, short, _cls)

    # Build a lightweight rpc namespace: prefer canonical_name(tab, verb) but
    # also support alias/custom ids like "Resource.alias" registered by op_wiring.
    rpc_ns = SimpleNamespace()
    for _verb in dir(methods_ns):
        if _verb.startswith("_"):
            continue
        candidates = (
            canonical_name(tab, _verb),
            f"{resource}.{_verb}",
        )
        _rpc_fn = None
        for _mid in candidates:
            try:
                _rpc_fn = self.rpc[_mid]
                break
            except KeyError:
                continue
        if _rpc_fn is not None:
            setattr(rpc_ns, _verb, _rpc_fn)

    # Routers on the model (latest binding wins on the class; all kept per-API in bindings)
    router_ns = SimpleNamespace(
        flat=flat_router,
        nested=(routers[1] if len(routers) > 1 else None),
    )

    # Publish onto the un-instantiated declarative model class
    setattr(decl, "schemas",       schemas_ns)
    setattr(decl, "methods",       methods_ns)
    setattr(decl, "rpc",           rpc_ns)
    setattr(decl, "core",          core_ns)
    setattr(decl, "core_raw",      core_raw_ns)
    setattr(decl, "handlers",      methods_ns)   # convenience alias
    setattr(decl, "raw_handlers",  core_ns)      # convenience alias
    setattr(decl, "router",        router_ns)
    # (Optional) columns mirror for quick introspection
    try:
        setattr(decl, "columns", {c.key: c for c in model.__table__.columns})
    except Exception:
        pass

    # Keep a per-AutoAPI binding registry to avoid collisions when multiple APIs bind the same model
    _b = getattr(decl, "__autoapi__", None)
    if _b is None:
        _b = SimpleNamespace()
        setattr(decl, "__autoapi__", _b)
    if not hasattr(_b, "bindings"):
        _b.bindings = {}
    _b.bindings[id(self)] = dict(
        schemas=schemas_ns,
        methods=methods_ns,
        rpc=rpc_ns,
        core=core_ns,
        core_raw=core_raw_ns,
        router=router_ns,
    )

    print(f"Bound helpers onto {decl.__name__}: schemas/methods/rpc/core/core_raw/router")
    # ─────────────────────────────────────────────────────────────────

    print(f"Routes registered for {resource}")
