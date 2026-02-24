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
        normalized = dict(params)
        nested = normalized.get("params")
        if set(normalized) == {"params"} and isinstance(nested, Mapping):
            return dict(nested)
        return normalized
    if isinstance(params, Sequence) and not isinstance(params, (str, bytes)):
        return list(params)
    raise HTTPException(
        status_code=400, detail="Invalid params: expected object or array"
    )


def _normalize_deps(deps: Optional[Sequence[Any]]) -> list:
    out = []
    for d in deps or ():
        try:
            is_dep_obj = hasattr(d, "dependency")
        except Exception:
            is_dep_obj = False
        out.append(d if is_dep_obj else Depends(d))
    return out


__all__ = [
    "_ok",
    "_err",
    "_normalize_params",
    "_normalize_deps",
]
