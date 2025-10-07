from __future__ import annotations
from typing import Callable, Mapping, Any, Dict
from .spec import ComponentSpec

# -------- JSON (de)serialization --------


def to_dict(spec: ComponentSpec) -> dict:
    return {
        "role": spec.role,
        "module": spec.module,
        "export": spec.export,
        "version": spec.version,
        "defaults": dict(spec.defaults),
    }


def from_dict(obj: Mapping[str, Any]) -> ComponentSpec:
    return ComponentSpec(
        role=str(obj["role"]),
        module=str(obj["module"]),
        export=str(obj.get("export", "default")),
        version=str(obj.get("version", "1.0.0")),
        defaults=dict(obj.get("defaults", {})),
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
