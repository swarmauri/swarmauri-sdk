from __future__ import annotations

from peagen.plugin_registry import registry
from .base import ResultBackend


def make_backend(provider: str, **kwargs) -> ResultBackend:
    try:
        cls = registry["result_backends"][provider]
    except KeyError:
        raise ValueError(
            f"No ResultBackend registered for provider '{provider}'"
        )
    return cls(**kwargs)


def __getattr__(name: str):
    if name == "ResultBackend":
        return ResultBackend
    raise AttributeError(name)
