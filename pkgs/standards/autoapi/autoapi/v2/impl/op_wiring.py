from __future__ import annotations
from typing import Any, Iterable, Type, List
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from .schema import _schema
from .rpc_adapter import _wrap_rpc
from ..ops.spec import OpSpec
from ..ops.registry import get_registered_ops
from ..types.op_config_provider import OpConfigProvider
from ..types.op_verb_alias_provider import OpVerbAliasProvider  # back-compat
from ..hooks import Phase

def _arity_for(target: str) -> str:
    return "collection" if target in {"create","list","bulk_create","bulk_update","bulk_replace","bulk_delete","clear"} else "member"

def collect_all_specs_for_table(table: Type) -> List[OpSpec]:
    out: List[OpSpec] = []
    # 1) class-declared specs
    if issubclass(table, OpConfigProvider):
        out.extend(list(getattr(table, "__autoapi_ops__", ()) or []))
    # 2) method decorators (custom_op)
    for name in dir(table):
        meth = getattr(table, name, None)
        tag: OpSpec | None = getattr(meth, "__autoapi_custom_op__", None)
        if tag:
            out.append(OpSpec(**{**tag.__dict__, "table": table, "handler": meth}))
    # 3) imperative registry (highest precedence)
    out.extend(get_registered_ops(table))
    # 4) back-compat: __autoapi_verb_aliases__ → specs
    if issubclass(table, OpVerbAliasProvider):
        raw = getattr(table, "__autoapi_verb_aliases__", {}) or {}
        if callable(raw): raw = raw()
        for tgt, alias in dict(raw).items():
            out.append(OpSpec(alias=alias, target=tgt, table=table))
    # fill defaults
    final: List[OpSpec] = []
    for s in out:
        final.append(OpSpec(
            alias=s.alias, target=s.target, table=table,
            expose_routes=s.expose_routes, expose_rpc=s.expose_rpc, expose_method=s.expose_method,
            arity=s.arity or _arity_for(s.target), persist=s.persist, returns=s.returns,
            handler=s.handler, request_model=s.request_model, response_model=s.response_model,
            http_methods=s.http_methods, path_suffix=s.path_suffix, tags=s.tags,
            rbac_guard_op=s.rbac_guard_op or s.target, hooks=s.hooks,
        ))
    return final

def _http_methods(spec: OpSpec) -> list[str]:
    if spec.http_methods: return list(spec.http_methods)
    return {
        "read":["GET"], "list":["GET"], "delete":["DELETE"],
        "update":["PATCH"], "replace":["PUT"], "create":["POST"],
        "bulk_create":["POST"], "bulk_update":["PATCH"], "bulk_replace":["PUT"], "bulk_delete":["DELETE"],
        "clear":["DELETE"],
    }.get(spec.target, ["POST"])

def _rest_path(table: Type, spec: OpSpec) -> str:
    base = _schema(table).path
    if spec.target in {"bulk_create","bulk_update","bulk_replace","bulk_delete"}:
        return f"{base}/bulk"
    if spec.target == "custom":
        if spec.arity == "member": return f"{base}/{{item_id}}/{spec.path_suffix or spec.alias}"
        return f"{base}/{spec.path_suffix or spec.alias}"
    if spec.arity == "member":
        return f"{base}/{{item_id}}"
    return base

def _in_model(table: Type, spec: OpSpec):
    return spec.request_model or _schema(table, verb=(spec.target if spec.target!="custom" else "create"))

def _out_model(table: Type, spec: OpSpec):
    if spec.returns == "raw":
        return spec.response_model or None
    if spec.target == "create":  # your builder uses None for create REST response_model
        return spec.response_model or None
    # default to canonical target
    return spec.response_model or _schema(table, verb=("read" if spec.target=="delete" else spec.target))

def attach_op_specs(api, router, table: Type) -> None:
    """
    Mount OpSpec-defined verbs across:
      - routes
      - rpc
      - methods
    """
    specs = collect_all_specs_for_table(table)
    pk = next(iter(table.__table__.primary_key.columns)).name

    for spec in specs:
        # REST
        if spec.expose_routes:
            In  = _in_model(table, spec)
            Out = _out_model(table, spec)

            # choose DB dep style identical to canonical (we inspect api.get_db/get_async_db in routes_builder)
            is_async = bool(api.get_async_db) if api.get_db is None else issubclass(table, api._include.__class__)  # trivial heuristic; reuse routes_builder's exact check if desired

            DBDep = (Depends(api.get_async_db) if is_async else Depends(api.get_db))
            def _DB(db): return db  # sentinel to keep Annotated out; we only need kw name

            async def _handler(request: Request, p: In = Depends(In), db = DBDep):
                # ctx enrichment for per-verb control
                if getattr(request.state, "ctx", None) is None:
                    request.state.ctx = {}
                request.state.ctx["__op_alias__"] = spec.alias
                request.state.ctx["__op_target__"] = spec.target
                request.state.ctx["__op_persist_policy__"] = spec.persist
                if spec.persist == "skip":
                    request.state.ctx["__autoapi_skip_persist__"] = True
                # run per-verb pre-hooks
                for h in sorted([x for x in spec.hooks if x.phase.name=="PRE_TX_BEGIN"], key=lambda x:x.order):
                    if h.when is None or h.when(request.state.ctx):
                        await h.fn(table=table, ctx=request.state.ctx, db=db, request=request, payload=p)
                # delegate to canonical RPC method id (or a custom one we register just below)
                method_id = f"{table.__name__}.{(spec.target if spec.target!='custom' else spec.alias).title().replace('_','')}"
                from ..jsonrpc_models import _RPCReq
                env = _RPCReq(id=None, method=method_id, params=p)
                ctx = {"request": request, "db": db, "env": env, "params": env.params}
                ext = getattr(request.state, "ctx", None)
                if isinstance(ext, dict): ctx.update(ext)
                # use the unified engine
                from ._runner import _invoke
                result = await _invoke(api, env.method, params=env.params, ctx=ctx)
                # run per-verb post-hooks
                for h in sorted([x for x in spec.hooks if x.phase.name=="POST_TX_END"], key=lambda x:x.order):
                    if h.when is None or h.when(ctx):
                        await h.fn(table=table, ctx=ctx, db=db, request=request, payload=p)
                return result

            router.add_api_route(
                _rest_path(table, spec), _handler, methods=_http_methods(spec),
                response_model=Out, tags=list(spec.tags or (table.__name__,)),
                name=f"{table.__name__} - {spec.alias}",
                summary=f"{table.__name__} - {spec.alias}",
            )

        # RPC
        if spec.expose_rpc:
            # If target is canonical → point alias to existing core (IN/OUT auto)
            # If custom/override → we still wrap the provided handler as a core
            if spec.target == "custom" and spec.handler:
                IN  = _in_model(table, spec)
                OUT = _out_model(table, spec)
                # normalize handler to (payload, db) signature
                async def _core(payload, db, _h=spec.handler):
                    return await _h(table, ctx={}, db=db, request=None, payload=payload)
                name = f"{table.__name__}.{spec.alias.title().replace('_','')}"
                api._wrap_rpc(_core, IN, OUT, pk, table)
                api._method_ids[name] = api._method_ids.get(name)  # _wrap_rpc already registers into api.rpc
            else:
                # alias → canonical: register an extra method id that points to the same core
                # (we reuse the existing canonical core via its method id)
                canon = f"{table.__name__}.{spec.target.title().replace('_','')}"
                alias = f"{table.__name__}.{spec.alias.title().replace('_','')}"
                api._method_ids[alias] = api._method_ids[canon]

        # METHODS
        if spec.expose_method:
            async def _callable(db, request, payload):
                from ..jsonrpc_models import _RPCReq
                method_id = f"{table.__name__}.{(spec.target if spec.target!='custom' else spec.alias).title().replace('_','')}"
                env = _RPCReq(id=None, method=method_id, params=payload)
                ctx = {"request": request, "db": db, "env": env, "params": env.params}
                from ._runner import _invoke
                return await _invoke(api, env.method, params=env.params, ctx=ctx)
            setattr(api.core, f"{table.__name__}{spec.alias.title().replace('_','')}", _callable)
            # do not overwrite self.methods; canonical wiring already attaches helpers there
