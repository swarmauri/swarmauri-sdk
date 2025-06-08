from __future__ import annotations

from importlib import import_module
from typing import Any, Dict, Optional


def resolve_plugin_spec(group: str, ref: str) -> Any:
    """Return the object referenced by ``ref`` within ``group``."""
    obj = registry.get(group, {}).get(ref)
    if obj is not None:
        return obj
    if group == "llms" and "." not in ref:
        class_name = "".join(part.capitalize() for part in ref.split("_")) + "Model"
        module = import_module(f"swarmauri.llms.{class_name}")
        return getattr(module, class_name)
    mod, cls = ref.split(":", 1) if ":" in ref else ref.rsplit(".", 1)
    module = import_module(mod)
    return getattr(module, cls)

from .plugins import discover_and_register_plugins, registry


class PluginManager:
    """Centralised plugin loader.

    ``PluginManager`` discovers entry-point plugins according to the mode set in
    ``.peagen.toml`` and instantiates only those plugins configured in the same
    file.  All plugin groups are handled generically so new groups can be added
    without modifying this class.
    """

    # ------------------------------------------------------------------
    # Mapping of plugin group -> config layout
    # ------------------------------------------------------------------
    GROUP_CONFIG: Dict[str, Dict[str, Optional[str]]] = {
        "storage_adapters": {
            "section": "storage",
            "items": "adapters",
            "default": "default_storage_adapter",
        },
        "publishers": {
            "section": "publishers",
            "items": "adapters",
            "default": "default_publisher",
        },
        "queues": {
            "section": "queues",
            "items": "adapters",
            "default": "default_queue",
        },
        "result_backends": {
            "section": "result_backends",
            "items": "adapters",
            "default": "default_backend",
        },
        "evaluators": {
            "section": "evaluation",
            "items": "evaluators",
            "default": None,
        },
        "evaluator_pools": {
            "section": "evaluation",
            "single": "pool",
            "default": None,
        },
        "template_sets": {
            "section": "workspace",
            "items": "template_sets",
            "default": "template_set",
        },
        "consumers": {"section": "consumers", "items": "plugins", "default": "default_consumer"},
        "indexers": {"section": "indexers", "items": "plugins", "default": "default_indexer"},
        "mutators": {"section": "mutators", "items": "plugins", "default": "default_mutator"},
        "programs": {"section": "programs", "items": "plugins", "default": "default_program"},
        "selectors": {"section": "selectors", "items": "plugins", "default": "default_selector"},
        "llms": {
            "section": "llm",
            "default": "default_provider",
        },
    }

    def __init__(self, cfg: Dict[str, Any]) -> None:
        plugins_cfg = cfg.get("plugins", {})
        mode = plugins_cfg.get("mode", "fan-out")
        switch_map = plugins_cfg.get("switch", {})
        discover_and_register_plugins(mode=mode, switch_map=switch_map)
        self.cfg = cfg

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------

    def _instantiate(self, cls_or_obj: Any, params: Dict[str, Any]) -> Any:
        return cls_or_obj(**params) if isinstance(cls_or_obj, type) else cls_or_obj

    def _layout(self, group: str) -> Dict[str, Optional[str]]:
        return self.GROUP_CONFIG.get(group, {"section": group, "items": "plugins", "default": "default"})

    def _group_cfg(self, group: str) -> Dict[str, Any]:
        info = self._layout(group)
        return self.cfg.get(info["section"], {})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get(self, group: str, name: Optional[str] = None) -> Any:
        """Return one plugin instance from ``group``."""

        layout = self._layout(group)
        cfg = self._group_cfg(group)

        if group == "llms":
            provider = name or cfg.get("default_provider")
            if not provider:
                raise KeyError("No plugin name provided for group 'llms'")
            params = cfg.get(provider, {})
            api_key = params.get("API_KEY") or params.get("api_key")
            model_name = cfg.get("default_model_name")
            temperature = cfg.get("default_temperature")
            max_tokens = cfg.get("default_max_tokens")
            from .core._llm import GenericLLM

            llm_mgr = GenericLLM()
            kwargs: Dict[str, Any] = {}
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            return llm_mgr.get_llm(
                provider=provider,
                api_key=api_key,
                model_name=model_name,
                **kwargs,
            )

        # single reference style
        if "single" in layout:
            ref = name or cfg.get(layout["single"])
            if not ref:
                raise KeyError(f"No plugin configured for group '{group}'")
            params = cfg.get(f"{layout['single']}_params", {})
            return self._instantiate(resolve_plugin_spec(group, ref), params)

        # dict of plugin specs
        items = cfg.get(layout.get("items", "plugins"), {})
        if name is None:
            default_key = layout.get("default")
            name = cfg.get(default_key) if default_key else None
        if not name:
            raise KeyError(f"No plugin name provided for group '{group}'")
        params = items.get(name, {})
        return self._instantiate(resolve_plugin_spec(group, name), params)

    def all(self, group: str) -> Dict[str, Any]:
        """Instantiate every configured plugin for ``group``."""

        layout = self._layout(group)
        cfg = self._group_cfg(group)

        if "single" in layout:
            ref = cfg.get(layout["single"])
            if not ref:
                return {}
            params = cfg.get(f"{layout['single']}_params", {})
            return {ref: self._instantiate(resolve_plugin_spec(group, ref), params)}

        items = cfg.get(layout.get("items", "plugins"), {})
        out: Dict[str, Any] = {}
        for name, params in items.items():
            out[name] = self._instantiate(resolve_plugin_spec(group, name), params)
        return out
