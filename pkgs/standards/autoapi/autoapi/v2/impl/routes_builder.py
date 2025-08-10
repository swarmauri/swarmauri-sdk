"""
autoapi/v2/routes_builder.py  –  Route building functionality for AutoAPI.

This module contains the logic for building both REST and RPC routes from
CRUD operations, including nested routing and RBAC guards.
"""

from __future__ import annotations

import functools
import inspect
import re
from typing import Annotated, Any, List

from fastapi import APIRouter, Body, Depends, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ._runner import _invoke
from ..jsonrpc_models import _RPCReq, create_standardized_error
from ..mixins import AsyncCapable, BulkCapable, Replaceable
from .rpc_adapter import _wrap_rpc
from .schema import _schema


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


def _register_routes_and_rpcs(  # noqa: N802 – bound as method
    self,
    model: type,
    tab: str,
    pk: str,
    SCreate,
    SReadOut,     # ← read OUTPUT schema
    SReadIn,      # ← read INPUT (pk-only) schema
    SDeleteIn,    # ← delete INPUT (pk-only) schema
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

    pk_col = next(iter(model.__table__.primary_key.columns))
    pk_type = getattr(pk_col.type, "python_type", str)

    # ---------- verb specification -----------------------------------
    spec: List[tuple] = [
        ("create", "POST",  "",          201, SCreate,             SReadOut,         _create),
        ("list",   "GET",   "",          200, SListIn,             List[SReadOut],   _list),
        ("clear",  "DELETE","",          204, None,                None,             _clear),
        ("read",   "GET",   "/{item_id}",200, SReadIn,             SReadOut,         _read),
        ("update", "PATCH", "/{item_id}",200, SUpdate,             SReadOut,         _update),
        ("delete", "DELETE","/{item_id}",204, SDeleteIn,           None,             _delete),
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
        spec += [
            ("bulk_create", "POST",   "/bulk", 201, List[SCreate],   List[SReadOut], _create),
            ("bulk_delete", "DELETE", "/bulk", 204, List[SDeleteIn], None,           _delete),
        ]

    # ---------- nested routing ---------------------------------------
    raw_pref = self._nested_prefix(model) or ""
    nested_pref = re.sub(r"/{2,}", "/", raw_pref).rstrip("/") or None
    nested_vars = re.findall(r"{(\w+)}", raw_pref)
    print(f"Nested prefix: {nested_pref} vars: {nested_vars}")

    allow_cb = getattr(model, "__autoapi_allow_anon__", None)
    _allow_verbs = set(allow_cb()) if callable(allow_cb) else set()
    self._allow_anon.update({_canonical(tab, v) for v in _allow_verbs})
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
            if self.authorize and not self.authorize(scope, request):
                print(f"Authorization failed for scope {scope}")
                http_exc, _, _ = create_standardized_error(403, rpc_code=-32095)
                raise http_exc

        return Depends(inner)

    # ---------- endpoint factory -------------------------------------
    for verb, http, path, status, In, Out, core in spec:
        m_id = _canonical(tab, verb)

        # RPC input model for adapter (distinct from REST signature)
        rpc_in = In or dict
        if verb in {"update", "replace"}:
            # For update/replace we want the verb-specific model (respects no_update flags)
            rpc_in = _schema(model, verb=verb)

        def _factory(
            is_nested_router, *, verb=verb, path=path, In=In, core=core, m_id=m_id
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

            # primary key path var
            if "{item_id}" in path:
                params.append(
                    inspect.Parameter(
                        "item_id",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=pk_type,
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
            elif In is not None and verb not in ("read", "delete", "clear"):
                params.append(
                    inspect.Parameter(
                        "p",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[_visible(In), Body(embed=False)],
                    )
                )

            # DB session
            params.append(
                inspect.Parameter(
                    "db",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Depends(provider)],
                )
            )

            # ---- callable body ---------------------------------------
            async def _impl(**kw):
                print(f"Endpoint {m_id} invoked with {kw}")
                db: Session | AsyncSession = kw.pop("db")
                req: Request = kw.pop("request")
                p = kw.pop("p", None)
                item_id = kw.pop("item_id", None)
                parent_kw = {k: kw[k] for k in nested_vars if k in kw}

                # assemble RPC-style param dict
                match verb:
                    case "read" | "delete":
                        rpc_params = {pk: item_id}
                    case "update" | "replace":
                        rpc_params = {pk: item_id, **p.model_dump(exclude_unset=True)}
                    case "list":
                        rpc_params = p.model_dump()
                    case _:
                        rpc_params = p.model_dump() if p is not None else {}

                if parent_kw:
                    rpc_params.update(parent_kw)

                print(f"RPC params built: {rpc_params}")
                env = _RPCReq(id=None, method=m_id, params=rpc_params)
                ctx = {"request": req, "db": db, "env": env, "params": env.params}

                def _build_args(_p):
                    match verb:
                        case "create" | "bulk_create" | "bulk_delete" | "list":
                            if verb == "list":
                                return (In(**_p),)
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
            deps = [_guard(m_id)]
            if m_id not in self._allow_anon:
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
            )

        # ─── register schemas on API namespace (for discovery / testing) ──
        for s in (In, Out, rpc_in):
            if not isinstance(s, type):
                continue
            name = s.__name__
            if name not in self._schemas:
                self._schemas[name] = s
                setattr(self.schemas, name, s)

        # JSON-RPC shim
        rpc_fn = _wrap_rpc(core, rpc_in, Out, pk, model)
        print(f"Registered RPC method {m_id} with IN={getattr(rpc_in, '__name__', rpc_in)} OUT={getattr(Out, '__name__', Out)}")
        self.rpc[m_id] = rpc_fn

        # ── in-process convenience wrapper ────────────────────────────────
        camel = f"{''.join(w.title() for w in tab.split('_'))}{''.join(w.title() for w in verb.split('_'))}"

        def _runner(payload, *, db=None, _method=m_id, _api=self):
            """
            Helper so you can call:  api.methods.UserCreate(SUserCreate(...))
            """
            if db is None:  # auto-open sync session
                if _api.get_db is None:
                    raise TypeError(
                        "Supply a Session via db=... "
                        "or register get_db when constructing AutoAPI()"
                    )
                gen = _api.get_db()
                db = next(gen)
                try:
                    return _api.rpc[_method](payload, db)
                finally:
                    try:
                        next(gen)  # finish generator → close
                    except StopIteration:
                        pass
            else:
                return _api.rpc[_method](payload, db)

        # Register under canonical id and camel helper
        self._method_ids[m_id] = _runner
        setattr(self.methods, camel, _runner)
        print(f"Registered helper method {camel}")

    # include routers
    self.router.include_router(flat_router)
    if len(routers) > 1:
        self.router.include_router(routers[1])
    print(f"Routes registered for {tab}")
