"""Backward-compatible application namespace."""

__all__ = ["App", "defineAppSpec", "deriveApp"]


def __getattr__(name: str):
    if name == "App":
        from ._app import App

        return App
    if name in {"defineAppSpec", "deriveApp"}:
        from .shortcuts import defineAppSpec, deriveApp

        return {"defineAppSpec": defineAppSpec, "deriveApp": deriveApp}[name]
    raise AttributeError(name)
