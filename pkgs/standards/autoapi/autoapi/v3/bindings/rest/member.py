from __future__ import annotations
import logging

import inspect
from types import SimpleNamespace
from typing import (
    Annotated,
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
    Optional,
    Sequence,
)

from .common import (
    AUTOAPI_AUTH_CONTEXT_ATTR,
    Body,
    Depends,
    HTTPException,
    Path,
    Request,
    OpSpec,
    _coerce_parent_kw,
    _get_phase_chains,
    _pk_name,
    _pk_names,
    _request_model_for,
    _serialize_output,
    _validate_body,
    _executor,
    _status,
)


logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/member")


def _make_member_endpoint(
    model: type,
    sp: OpSpec,
    *,
    resource: str,
    db_dep: Callable[..., Any],
    pk_param: str = "item_id",
    nested_vars: Sequence[str] | None = None,
    api: Any | None = None,
) -> Callable[..., Awaitable[Any]]:
    alias = sp.alias
    target = sp.target
    real_pk = _pk_name(model)
    pk_names = _pk_names(model)
    nested_vars = list(nested_vars or [])

    # --- No body on GET read / DELETE delete ---
    if target in {"read", "delete"}:

        async def _endpoint(
            item_id: Any,
            request: Request,
            db: Any = Depends(db_dep),
            **kw: Any,
        ):
            parent_kw = {k: kw[k] for k in nested_vars if k in kw}
            _coerce_parent_kw(model, parent_kw)
            payload: Mapping[str, Any] = dict(parent_kw)
            path_params = {real_pk: item_id, pk_param: item_id, **parent_kw}
            ctx: Dict[str, Any] = {
                "request": request,
                "db": db,
                "payload": payload,
                "path_params": path_params,
                # expose contextual metadata for downstream atoms
                "app": getattr(request, "app", None),
                "api": getattr(request, "app", None),
                "model": model,
                "op": alias,
                "method": alias,
                "target": target,
                "env": SimpleNamespace(
                    method=alias, params=payload, target=target, model=model
                ),
                "api": api,
                "model": model,
                "op": alias,
            }
            ac = getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, None)
            if ac is not None:
                ctx["auth_context"] = ac
            ctx["response_serializer"] = lambda r: _serialize_output(
                model, alias, target, sp, r
            )
            phases = _get_phase_chains(model, alias)
            result = await _executor._invoke(
                request=request,
                db=db,
                phases=phases,
                ctx=ctx,
            )
            return result

        params = [
            inspect.Parameter(
                nv,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[str, Path(...)],
            )
            for nv in nested_vars
        ]
        params.extend(
            [
                inspect.Parameter(
                    "item_id",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Path(...)],
                ),
                inspect.Parameter(
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                ),
                inspect.Parameter(
                    "db",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Depends(db_dep)],
                ),
            ]
        )
        _endpoint.__signature__ = inspect.Signature(params)

        _endpoint.__name__ = f"rest_{model.__name__}_{alias}_member"
        _endpoint.__qualname__ = _endpoint.__name__
        _endpoint.__doc__ = (
            f"REST member endpoint for {model.__name__}.{alias} ({target})"
        )
        # NOTE: do NOT set body annotation for no-body endpoints
        return _endpoint

    body_model = _request_model_for(sp, model)
    if body_model is None and sp.request_model is None and target == "custom":

        async def _endpoint(
            item_id: Any,
            request: Request,
            db: Any = Depends(db_dep),
            **kw: Any,
        ):
            parent_kw = {k: kw[k] for k in nested_vars if k in kw}
            _coerce_parent_kw(model, parent_kw)
            payload: Mapping[str, Any] = dict(parent_kw)
            path_params = {real_pk: item_id, pk_param: item_id, **parent_kw}
            ctx: Dict[str, Any] = {
                "request": request,
                "db": db,
                "payload": payload,
                "path_params": path_params,
                # expose contextual metadata for downstream atoms
                "app": getattr(request, "app", None),
                "api": getattr(request, "app", None),
                "model": model,
                "op": alias,
                "method": alias,
                "target": target,
                "env": SimpleNamespace(
                    method=alias, params=payload, target=target, model=model
                ),
                "api": api,
                "model": model,
                "op": alias,
            }
            ac = getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, None)
            if ac is not None:
                ctx["auth_context"] = ac
            ctx["response_serializer"] = lambda r: _serialize_output(
                model, alias, target, sp, r
            )
            phases = _get_phase_chains(model, alias)
            result = await _executor._invoke(
                request=request,
                db=db,
                phases=phases,
                ctx=ctx,
            )
            return result

        params = [
            inspect.Parameter(
                nv,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[str, Path(...)],
            )
            for nv in nested_vars
        ]
        params.extend(
            [
                inspect.Parameter(
                    "item_id",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Path(...)],
                ),
                inspect.Parameter(
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                ),
                inspect.Parameter(
                    "db",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Depends(db_dep)],
                ),
            ]
        )
        _endpoint.__signature__ = inspect.Signature(params)

        _endpoint.__name__ = f"rest_{model.__name__}_{alias}_member"
        _endpoint.__qualname__ = _endpoint.__name__
        _endpoint.__doc__ = (
            f"REST member endpoint for {model.__name__}.{alias} ({target})"
        )
        return _endpoint

    # --- Body-based member endpoints: PATCH update / PUT replace (and custom member) ---

    if body_model is None:
        body_annotation = Optional[Mapping[str, Any]]
        body_default = Body(None)
    else:
        body_annotation = body_model
        body_default = Body(...)

    async def _endpoint(
        item_id: Any,
        request: Request,
        db: Any = Depends(db_dep),
        body=body_default,
        **kw: Any,
    ):
        parent_kw = {k: kw[k] for k in nested_vars if k in kw}
        _coerce_parent_kw(model, parent_kw)
        payload = _validate_body(model, alias, target, body)

        # Enforce path-PK canonicality. If body echoes PK: drop if equal, 409 if mismatch.
        for k in pk_names:
            if k in payload:
                if str(payload[k]) != str(item_id) and len(pk_names) == 1:
                    raise HTTPException(
                        status_code=_status.HTTP_409_CONFLICT,
                        detail=f"Identifier mismatch for '{k}': path={item_id}, body={payload[k]}",
                    )
                payload.pop(k, None)
        payload.pop(pk_param, None)
        if parent_kw:
            payload.update(parent_kw)

        path_params = {real_pk: item_id, pk_param: item_id, **parent_kw}

        ctx: Dict[str, Any] = {
            "request": request,
            "db": db,
            "payload": payload,
            "path_params": path_params,
            # expose contextual metadata for downstream atoms
            "app": getattr(request, "app", None),
            "api": getattr(request, "app", None),
            "model": model,
            "op": alias,
            "method": alias,
            "target": target,
            "env": SimpleNamespace(
                method=alias, params=payload, target=target, model=model
            ),
        }
        ac = getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, None)
        if ac is not None:
            ctx["auth_context"] = ac
        ctx["response_serializer"] = lambda r: _serialize_output(
            model, alias, target, sp, r
        )
        phases = _get_phase_chains(model, alias)
        result = await _executor._invoke(
            request=request,
            db=db,
            phases=phases,
            ctx=ctx,
        )
        return result

    params = [
        inspect.Parameter(
            nv,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[str, Path(...)],
        )
        for nv in nested_vars
    ]
    params.extend(
        [
            inspect.Parameter(
                "item_id",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[Any, Path(...)],
            ),
            inspect.Parameter(
                "request",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Request,
            ),
            inspect.Parameter(
                "db",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[Any, Depends(db_dep)],
            ),
            inspect.Parameter(
                "body",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=body_annotation,
                default=body_default,
            ),
        ]
    )
    _endpoint.__signature__ = inspect.Signature(params)

    _endpoint.__name__ = f"rest_{model.__name__}_{alias}_member"
    _endpoint.__qualname__ = _endpoint.__name__
    _endpoint.__doc__ = f"REST member endpoint for {model.__name__}.{alias} ({target})"
    _endpoint.__annotations__["body"] = body_annotation
    return _endpoint
