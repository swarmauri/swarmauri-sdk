from __future__ import annotations

import inspect
import logging
from typing import Annotated, Any, Awaitable, Callable, Mapping, Optional, Sequence

from .common import (
    Body,
    Depends,
    HTTPException,
    OpSpec,
    Path,
    Request,
    _coerce_parent_kw,
    _pk_name,
    _pk_names,
    _request_model_for,
    _status,
    _validate_body,
)
from .io_headers import _make_header_dep

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/rest/member")


def _make_member_endpoint(
    model: type,
    sp: OpSpec,
    *,
    resource: str,
    db_dep: Callable[..., Any],
    pk_param: str = "item_id",
    nested_vars: Sequence[str] | None = None,
    router: Any | None = None,
) -> Callable[..., Awaitable[Any]]:
    del resource

    alias = sp.alias
    target = sp.target
    real_pk = _pk_name(model)
    pk_names = _pk_names(model)
    nested_vars = list(nested_vars or [])
    hdr_dep = _make_header_dep(model, alias)

    if target in {"read", "delete"}:

        async def _endpoint(
            item_id: Any,
            request: Request,
            db: Any = Depends(db_dep),
            h: Mapping[str, Any] = Depends(hdr_dep),
            **kw: Any,
        ):
            del request, db
            parent_kw = {k: kw[k] for k in nested_vars if k in kw}
            _coerce_parent_kw(model, parent_kw)
            payload: Mapping[str, Any] = dict(parent_kw)
            if isinstance(h, Mapping):
                payload = {**payload, **dict(h)}
            path_params = {real_pk: item_id, pk_param: item_id, **parent_kw}
            return {
                "model": model,
                "alias": alias,
                "target": target,
                "payload": payload,
                "path_params": path_params,
                "router": router,
            }

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
        return _endpoint

    body_model = _request_model_for(sp, model)
    body_annotation = Optional[Mapping[str, Any]] if body_model is None else body_model
    body_default = Body(None) if body_model is None else Body(...)

    async def _endpoint(
        item_id: Any,
        request: Request,
        db: Any = Depends(db_dep),
        h: Mapping[str, Any] = Depends(hdr_dep),
        body=body_default,
        **kw: Any,
    ):
        del request, db

        parent_kw = {k: kw[k] for k in nested_vars if k in kw}
        _coerce_parent_kw(model, parent_kw)
        payload = _validate_body(model, alias, target, body)
        if isinstance(h, Mapping):
            payload = {**payload, **dict(h)}

        for key in pk_names:
            if key in payload:
                if str(payload[key]) != str(item_id) and len(pk_names) == 1:
                    raise HTTPException(
                        status_code=_status.HTTP_409_CONFLICT,
                        detail=(
                            f"Identifier mismatch for '{key}': "
                            f"path={item_id}, body={payload[key]}"
                        ),
                    )
                payload.pop(key, None)

        payload.pop(pk_param, None)
        if parent_kw:
            payload.update(parent_kw)

        path_params = {real_pk: item_id, pk_param: item_id, **parent_kw}
        return {
            "model": model,
            "alias": alias,
            "target": target,
            "payload": payload,
            "path_params": path_params,
            "router": router,
        }

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
