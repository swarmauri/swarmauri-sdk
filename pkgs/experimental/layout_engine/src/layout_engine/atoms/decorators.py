from __future__ import annotations
from functools import wraps
from typing import Any, Mapping

from .default import AtomRegistry
from .spec import AtomSpec


def atom_ctx(
    *,
    role: str,
    module: str,
    export: str = "default",
    version: str = "1.0.0",
    defaults: Mapping[str, Any] | None = None,
    registry: AtomRegistry | None = None,
):
    """Decorator to declare and optionally register an atom specification.

    Example:
        @atom_ctx(role="kpi", module="@app/widgets/Kpi.svelte", defaults={"format":"currency"}, registry=REG)
        def kpi(): pass
    """

    def deco(fn):
        spec = AtomSpec(
            role=role,
            module=module,
            export=export,
            version=version,
            defaults=defaults or {},
        )
        setattr(fn, "__atom_spec__", spec)
        if registry is not None:
            registry.register(spec)

        @wraps(fn)
        def wrapper(*a, **kw):
            return fn(*a, **kw)

        return wrapper

    return deco


def atom(
    *,
    role: str,
    module: str,
    export: str = "default",
    version: str = "1.0.0",
    defaults: Mapping[str, Any] | None = None,
    registry: AtomRegistry | None = None,
):
    """Decorator alias to register atoms inline."""
    return atom_ctx(
        role=role,
        module=module,
        export=export,
        version=version,
        defaults=defaults,
        registry=registry,
    )


def validate_props(schema: Mapping[str, Any] | None = None):
    """No-op validation decorator placeholder.

    Hook point for adding runtime schema validation (pydantic/jsonschema) in apps that need it,
    while keeping core package free of heavy deps.
    """

    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            # place to validate kw against schema if provided
            return fn(*a, **kw)

        return wrapper

    return deco
