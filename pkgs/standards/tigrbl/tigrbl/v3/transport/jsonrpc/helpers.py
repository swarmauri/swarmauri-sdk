from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence

try:
    from ...types import Depends, HTTPException
except Exception:  # pragma: no cover

    def Depends(fn):  # type: ignore
        return fn

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: Any = None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail


def _ok(result: Any, id_: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "result": result, "id": id_}


def _err(code: int, msg: str, id_: Any, data: Any | None = None) -> Dict[str, Any]:
    e: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "error": {"code": code, "message": msg},
        "id": id_,
    }
    if data is not None:
        e["error"]["data"] = data
    return e


def _normalize_params(params: Any) -> Any:
    if params is None:
        return {}
    if isinstance(params, Mapping):
        return dict(params)
    if isinstance(params, Sequence) and not isinstance(params, (str, bytes)):
        return list(params)
    raise HTTPException(
        status_code=400, detail="Invalid params: expected object or array"
    )


def _model_for(api: Any, name: str) -> Optional[type]:
    models: Dict[str, type] = getattr(api, "models", {}) or {}
    mdl = models.get(name)
    if mdl is not None:
        return mdl
    lower = name.lower()
    for k, v in models.items():
        if k.lower() == lower:
            return v
    return None


def _user_from_request(request: Any) -> Any | None:
    return getattr(request.state, "user", None)


def _select_auth_dep(api: Any):
    if getattr(api, "_optional_authn_dep", None):
        return api._optional_authn_dep
    if getattr(api, "_allow_anon", True) is False and getattr(api, "_authn", None):
        return api._authn
    if getattr(api, "_authn", None):
        return api._authn
    return None


def _normalize_deps(deps: Optional[Sequence[Any]]) -> list:
    out = []
    for d in deps or ():
        try:
            is_dep_obj = hasattr(d, "dependency")
        except Exception:
            is_dep_obj = False
        out.append(d if is_dep_obj else Depends(d))
    return out


def _authorize(
    api: Any,
    request: Any,
    model: type,
    alias: str,
    payload: Mapping[str, Any],
    user: Any | None,
):
    fn = getattr(api, "_authorize", None) or getattr(
        model, "__tigrbl_authorize__", None
    )
    if not fn:
        return
    try:
        rv = fn(request=request, model=model, alias=alias, payload=payload, user=user)
        if rv is False:
            raise HTTPException(status_code=403, detail="Forbidden")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=403, detail="Forbidden")


__all__ = [
    "_ok",
    "_err",
    "_normalize_params",
    "_model_for",
    "_user_from_request",
    "_select_auth_dep",
    "_normalize_deps",
    "_authorize",
]
