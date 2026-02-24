from __future__ import annotations


def build_router_and_attach(*args, **kwargs) -> None:
    del args, kwargs
    raise RuntimeError("Legacy REST endpoint builders have been removed from ingress.")
