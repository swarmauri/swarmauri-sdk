from __future__ import annotations
from typing import Any, Callable, Dict, Mapping

from .spec import AtomSpec

# -------- JSON (de)serialization --------


def atom_to_dict(spec: AtomSpec) -> dict:
    data = {
        "role": spec.role,
        "module": spec.module,
        "export": spec.export,
        "version": spec.version,
        "defaults": dict(spec.defaults),
    }
    if spec.family is not None:
        data["family"] = spec.family
    if spec.framework is not None:
        data["framework"] = spec.framework
    if spec.package is not None:
        data["package"] = spec.package
    if spec.tokens:
        data["tokens"] = dict(spec.tokens)
    if spec.registry:
        data["registry"] = dict(spec.registry)
    return data


def atom_from_dict(obj: Mapping[str, Any]) -> AtomSpec:
    return AtomSpec(
        role=str(obj["role"]),
        module=str(obj["module"]),
        export=str(obj.get("export", "default")),
        version=str(obj.get("version", "1.0.0")),
        defaults=dict(obj.get("defaults", {})),
        family=obj.get("family"),
        framework=obj.get("framework"),
        package=obj.get("package"),
        tokens=dict(obj.get("tokens", {})),
        registry=dict(obj.get("registry", {})),
    )


def registry_to_dict(registry) -> dict[str, dict]:
    return registry.dict()


def registry_from_dict(registry, data: Mapping[str, Mapping[str, Any]]) -> None:
    registry.update_from_dict(data)


# -------- Optional server render bindings (SSR partials) --------

Renderer = Callable[[Mapping[str, Any]], str]
HTMLRenderer = Renderer
SVGRenderer = Renderer


class ServerBindings:
    """Container for server-side renderers by (role, target).

    Example:
        bindings = ServerBindings()
        bindings.register("kpi", "html", lambda props: f"<div>{props['value']}</div>")
        html = bindings.render("kpi", "html", {"value": 123})
    """

    def __init__(self):
        self._map: Dict[str, Dict[str, Renderer]] = {}

    def register(self, role: str, target: str, renderer: Renderer) -> None:
        self._map.setdefault(role, {})[target] = renderer

    def has(self, role: str, target: str) -> bool:
        return role in self._map and target in self._map[role]

    def render(self, role: str, target: str, props: Mapping[str, Any]) -> str:
        try:
            fn = self._map[role][target]
        except KeyError:
            raise KeyError(f"No server renderer for role='{role}' target='{target}'")
        return fn(props)
