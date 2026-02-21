from __future__ import annotations
import logging

import inspect
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
    Body,
    Depends,
    HTTPException,
    Path,
    Request,
    OpSpec,
    _coerce_parent_kw,
    _is_http_response,
    _pk_name,
    _pk_names,
    _request_model_for,
    _serialize_output,
    _validate_body,
    _status,
    _status_for,
)

from .io_headers import _make_header_dep

from ...transport.dispatch import dispatch_operation


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
    status_code = _status_for(sp)
    real_pk = _pk_name(model)
    pk_names = _pk_names(model)
    nested_vars = list(nested_vars or [])
    hdr_dep = _make_header_dep(model, alias)

    # --- No body on GET read / DELETE delete ---
    if target in {"read", "delete"}:

        async def _endpoint(
            item_id: Any,
            request: Request,
            db: Any = Depends(db_dep),
            h: Mapping[str, Any] = Depends(hdr_dep),
            **kw: Any,
        ):
            parent_kw = {k: kw[k] for k in nested_vars if k in kw}
            _coerce_parent_kw(model, parent_kw)
            payload: Mapping[str, Any] = dict(parent_kw)
            if isinstance(h, Mapping):
                payload = {**payload, **dict(h)}
            path_params = {real_pk: item_id, pk_param: item_id, **parent_kw}
            seed_ctx: Dict[str, Any] = {}

            def _serializer(r, _ctx=seed_ctx):
                out = _serialize_output(model, alias, target, sp, r)
                temp = _ctx.get("temp", {}) if isinstance(_ctx, Mapping) else {}
                extras = (
                    temp.get("response_extras", {}) if isinstance(temp, Mapping) else {}
                )
                if isinstance(out, dict) and isinstance(extras, dict):
                    out.update(extras)
                return out

            result = await dispatch_operation(
                router=api,
                request=request,
                db=db,
                model_or_name=model,
                alias=alias,
                target=target,
                payload=payload,
                path_params=path_params,
                seed_ctx=seed_ctx,
                response_serializer=_serializer,
            )
            if _is_http_response(result):
                if sp.status_code is not None or result.status_code == 200:
                    result.status_code = status_code
                return result
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
                    pk_param,
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
                    "h",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Mapping[str, Any], Depends(hdr_dep)],
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
            seed_ctx: Dict[str, Any] = {}

            def _serializer(r, _ctx=seed_ctx):
                out = _serialize_output(model, alias, target, sp, r)
                temp = _ctx.get("temp", {}) if isinstance(_ctx, Mapping) else {}
                extras = (
                    temp.get("response_extras", {}) if isinstance(temp, Mapping) else {}
                )
                if isinstance(out, dict) and isinstance(extras, dict):
                    out.update(extras)
                return out

            result = await dispatch_operation(
                router=api,
                request=request,
                db=db,
                model_or_name=model,
                alias=alias,
                target=target,
                payload=payload,
                path_params=path_params,
                seed_ctx=seed_ctx,
                response_serializer=_serializer,
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
                    pk_param,
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
        h: Mapping[str, Any] = Depends(hdr_dep),
        body=body_default,
        **kw: Any,
    ):
        parent_kw = {k: kw[k] for k in nested_vars if k in kw}
        _coerce_parent_kw(model, parent_kw)
        payload = _validate_body(model, alias, target, body)
        if isinstance(h, Mapping):
            payload = {**payload, **dict(h)}

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

        seed_ctx: Dict[str, Any] = {}

        def _serializer(r, _ctx=seed_ctx):
            out = _serialize_output(model, alias, target, sp, r)
            temp = _ctx.get("temp", {}) if isinstance(_ctx, Mapping) else {}
            extras = (
                temp.get("response_extras", {}) if isinstance(temp, Mapping) else {}
            )
            if isinstance(out, dict) and isinstance(extras, dict):
                out.update(extras)
            return out

        result = await dispatch_operation(
            router=api,
            request=request,
            db=db,
            model_or_name=model,
            alias=alias,
            target=target,
            payload=payload,
            path_params=path_params,
            seed_ctx=seed_ctx,
            response_serializer=_serializer,
        )

        if _is_http_response(result):
            if sp.status_code is not None or result.status_code == 200:
                result.status_code = status_code
            return result
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
                pk_param,
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
                "h",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[Mapping[str, Any], Depends(hdr_dep)],
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
