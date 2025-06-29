from __future__ import annotations

from collections import namedtuple
from typing import Dict, Type

from pydantic import BaseModel

_MethodSpec = namedtuple("_MethodSpec", "params result")

_registry: Dict[str, _MethodSpec] = {}


def register(
    *, method: str, params_model: Type[BaseModel], result_model: Type[BaseModel]
):
    if method in _registry:
        raise RuntimeError(f"Duplicate JSON-RPC method name: {method}")
    _registry[method] = _MethodSpec(params_model, result_model)
    return method


def params_model(method: str) -> Type[BaseModel] | None:
    spec = _registry.get(method)
    return None if spec is None else spec.params


def result_model(method: str) -> Type[BaseModel] | None:
    spec = _registry.get(method)
    return None if spec is None else spec.result
