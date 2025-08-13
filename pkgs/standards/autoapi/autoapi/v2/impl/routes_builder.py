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

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..types import APIRouter, Depends, Request, Path, Body
from ._runner import _invoke
from ..jsonrpc_models import _RPCReq, create_standardized_error
from ..mixins import AsyncCapable, BulkCapable, Replaceable
from .rpc_adapter import _wrap_rpc
from .schema import _schema


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


def _canonical(tab: str, verb: str) -> str:
    """Return canonical RPC method name."""
    cls_name = "".join(w.title() for w in tab.split("_")) if tab.islower() else tab
    name = f"{cls_name}.{verb}"
    print(f"_canonical generated {name}")
    return name


def _resource_pascal(tab_or_cls: str) -> str:
    return (
        "".join(w.title() for w in tab_or_cls.split("_"))
        if tab_or_cls.islower()
        else tab_or_cls
    )


# ──────────────────────────────────────────────────────────────────────────────
# Verb aliasing (RPC exposure + helper names; REST paths unchanged)
# ──────────────────────────────────────────────────────────────────────────────

_VALID_VERBS = {
    "create",
    "read",
    "update",
    "delete",
    "list",
    "clear",
    "replace",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
}

_alias_re = re.compile(r"^[a-z][a-z0-9_]*$")


def _get_verb_alias_map(model) -> dict[str, str]:
    raw = getattr(model, "__autoapi_verb_aliases__", None)
    if callable(raw):
        raw = raw()
    return dict(raw or {})


def _alias_policy(model) -> str:
    # "both" | "alias_only" | "canonical_only"
    return getattr(model, "__autoapi_verb_alias_policy__", "both")


def _public_verb(model, canonical: str) -> str:
    ali = _get_verb_alias_map(model).get(canonical)
    if not ali or ali == canonical:
        return canonical
    if canonical not in _VALID_VERBS:
        raise RuntimeError(f"{model.__name__}: unsupported verb {canonical!r}")
    if not _alias_re.match(ali):
        raise RuntimeError(
            f"{model.__name__}.__autoapi_verb_aliases__: bad alias {ali!r} for {canonical!r} "
            "(must be lowercase [a-z0-9_], start with a letter)"
        )
    return ali


def _route_label(resource_name: str, verb: str, model) -> str:
    """Return '{Resource} - {verb/alias}' per policy."""
    pol = _alias_policy(model)
    pub = _public_verb(model, verb)
    if pol == "alias_only" and pub != verb:
        lab = pub
    elif pol == "both" and pub != verb:
        lab = f"{verb}/{pub}"
    else:
        lab = verb
    return f"{_resource_pascal(resource_name)} - {lab}"


# ──────────────────────────────────────────────────────────────────────────────


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
    self._allow_anon.update({_canonical(resource, v) for v in _allow_verbs})
    if _allow_verbs:
        print(f"Anon allowed verbs: {_allow_verbs}")

    flat_router = APIRouter(prefix=f"/{tab}", tags=[tab])
    routers = (
        (flat_router,)
        if nested_pref is None
        else (flat_router, APIRouter(prefix=nested_pref, tags=[f"nested-{tab}"]))
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
        m_id_canon = _canonical(resource, verb)

        # RPC input model for adapter (distinct from REST signature)
        rpc_in = In or dict
        if verb in {"update", "replace"}:
            # For update/replace we want the verb-specific model (respects no_update flags)
            rpc_in = _schema(model, verb=verb)

        # Route label (name/summary) using alias policy
        route_name = _route_label(resource, verb, model)

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
            elif verb == "clear" and issubclass(model, BulkCapable) and path == "":
                # allow optional body for bulk_delete on the "/" route if you adopt unified semantics later
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

            # DB session (dependency, not a query param; no Optional/union)
            params.append(
                inspect.Parameter(
                    "db",
                    inspect.Parameter.KEYWORD_ONLY,
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
                        return obj.model_dump(exclude_unset=True)
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
                            | "list"
                        ):
                            return (_p,)
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
                name=route_name,  # ← route name reflects alias policy
                summary=route_name,  # ← docs summary ditto
            )

        # ─── register schemas on API namespace (for discovery / testing) ──
        verb_camel = "".join(w.title() for w in verb.split("_"))
        for s, suffix in ((In, "In"), (Out, "Out"), (rpc_in, "RpcIn")):
            if not isinstance(s, type) or s is dict:
                continue
            canon = f"{resource}{verb_camel}{suffix}"
            if canon not in self._schemas:
                self._schemas[canon] = s
                setattr(self.schemas, canon, s)

            # Preserve legacy nested access (api.schemas.User.create)
            name = s.__name__
            base = model.__name__
            if not name.startswith(base):
                base = resource
            op = name[len(base) :]
            op = re.sub(r"(?<!^)(?=[A-Z])", "_", op).lstrip("_").lower() or "base"
            _attach(self.schemas, base, op, s)

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
                Helper so you can call:  api.methods.User.Create(...), api.methods.User.Register(...)
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
        camel = f"{resource}{''.join(w.title() for w in verb.split('_'))}"
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
                        o.model_dump(exclude_unset=True)
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

        # ── alias exposure per policy (RPC ids + helpers + core/core_raw) ─────
        pol = _alias_policy(model)
        pub = _public_verb(model, verb)
        if pub != verb and pol in ("both", "alias_only"):
            m_id_alias = _canonical(resource, pub)
            # Same rpc_fn handles alias
            self.rpc.add(m_id_alias, rpc_fn)

            alias_camel = f"{resource}{''.join(w.title() for w in pub.split('_'))}"
            _runner_alias = _make_runner(m_id_alias)
            self._method_ids[m_id_alias] = _runner_alias

            # Attach alias helpers (both global CamelCase and namespaced)
            setattr(self.core, alias_camel, core)
            _attach(self.core, resource, pub, core)

            _attach(self.methods, resource, pub, _runner_alias)
            setattr(self.core_raw, alias_camel, _core_raw)
            _attach(self.core_raw, resource, pub, _core_raw)

            print(f"Registered alias RPC id {m_id_alias} and helper {alias_camel}")

    # include routers
    self.router.include_router(flat_router)
    if len(routers) > 1:
        self.router.include_router(routers[1])
    print(f"Routes registered for {tab}")
