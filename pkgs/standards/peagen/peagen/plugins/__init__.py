# peagen/plugins.py
"""Plugin registry for the Peagen microkernel."""

from importlib.metadata import entry_points
from collections import defaultdict
from types import ModuleType
from typing import Any, Dict, Optional

from peagen.errors import InvalidPluginSpecError
from swarmauri_base.key_providers import KeyProviderBase
from swarmauri_base.git_filters import GitFilterBase
from swarmauri_base.crypto.CryptoBase import CryptoBase

# ---------------------------------------------------------------------------
# Config – group key → (entry-point group string, expected base class)
# ---------------------------------------------------------------------------
GROUPS = {
    # entry point groups
    # built-in implementations live under ``peagen.plugins``
    "consumers": ("peagen.plugins.consumers", object),
    "evaluator_pools": ("peagen.plugins.evaluator_pools", object),
    "evaluators": ("peagen.plugins.evaluators", object),
    "mutators": ("peagen.plugins.mutators", object),
    "programs": ("peagen.plugins.programs", object),
    "publishers": ("peagen.plugins.publishers", object),
    "queues": ("peagen.plugins.queues", object),
    # "result_backends": ("peagen.plugins.result_backends", object),
    # deprecated: storage adapters are now git filters
    "storage_adapters": ("peagen.plugins.storage_adapters", object),
    "git_filters": ("peagen.plugins.git_filters", GitFilterBase),
    "vcs": ("peagen.plugins.vcs", object),
    "selectors": ("peagen.plugins.selectors", object),
    # keys and secrets
    "cryptos": ("peagen.plugins.cryptos", CryptoBase),
    "key_providers": ("swarmauri.key_providers", KeyProviderBase),
    # template sets remain in the top-level package
    "template_sets": ("peagen.template_sets", None),
}

registry: Dict[str, Dict[str, object]] = defaultdict(dict)
_DISCOVERED = False


def discover_and_register_plugins(
    mode: str = "fan-out", switch_map: dict[str, str] | None = None
) -> None:
    """Discover entry-point plugins and register them.

    Parameters
    ----------
    mode:
        ``"fan-out"`` loads every discovered plugin. ``"fallback"`` prefers
        built-ins when names clash. ``"switch"`` only loads the plugin named in
        ``switch_map`` for each group, falling back to built-ins.
    switch_map:
        Optional mapping of ``group_key`` → ``plugin_name`` for ``"switch"`` mode.
    """

    global _DISCOVERED
    if _DISCOVERED:
        return

    switch_map = switch_map or {}

    for group_key, (ep_group, base_cls) in GROUPS.items():
        eps = list(entry_points(group=ep_group))
        builtins = [ep for ep in eps if ep.module.startswith("peagen.")]
        others = [ep for ep in eps if not ep.module.startswith("peagen.")]

        if mode == "switch":
            chosen = builtins[:]
            target = switch_map.get(group_key)
            if target:
                chosen.extend(ep for ep in others if ep.name == target)
            eps_to_process = chosen
        else:
            eps_to_process = builtins + others

        for ep in eps_to_process:
            obj = ep.load()

            if ep.name in registry[group_key]:
                existing = registry[group_key][ep.name]
                if existing is obj:
                    continue
                if mode == "fallback":
                    continue
                raise RuntimeError(
                    f"Duplicate plugin name '{ep.name}' detected in group '{group_key}'."
                )

            if group_key == "template_sets":
                if not (isinstance(obj, ModuleType) or isinstance(obj, type)):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{ep_group}' "
                        f"resolved to {type(obj).__name__}; expected a module or class."
                    )
            else:
                if not isinstance(obj, type):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{ep_group}' "
                        f"resolved to {type(obj).__name__}; expected a class."
                    )
                if not issubclass(obj, base_cls):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{ep_group}' must subclass {base_cls.__name__}."
                    )

            registry[group_key][ep.name] = obj

    _DISCOVERED = True


class PluginManager:
    """Centralised plugin loader for peagen plugins."""

    GROUP_CONFIG: Dict[str, Dict[str, Optional[str]]] = {
        # deprecated: use git_filters instead
        "storage_adapters": {
            "section": "storage",
            "items": "adapters",
            "default": "default_storage_adapter",
        },
        "git_filters": {
            "section": "storage",
            "items": "filters",
            "default": "default_filter",
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
        # "result_backends": {
        #     "section": "result_backends",
        #     "items": "adapters",
        #     "default": "default_backend",
        # },
        "evaluators": {
            "section": "evaluation",
            "items": "evaluators",
            "default": "default_evaluator",
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
        # "consumers": {
        #     "section": "consumers",
        #     "items": "plugins",
        #     "default": "default_consumer",
        # },
        "mutators": {
            "section": "mutation",
            "items": "mutators",
            "default": "default_mutator",
        },
        "programs": {
            "section": "programs",
            "items": "plugins",
            "default": "default_program",
        },
        "vcs": {
            "section": "vcs",
            "items": "adapters",
            "default": "default_vcs",
        },
        "selectors": {
            "section": "selectors",
            "items": "plugins",
            "default": "default_selector",
        },
        "llms": {
            "section": "llm",
            "default": "default_provider",
        },
        "cryptos": {
            "section": "cryptos",
            "items": "adapters",
            "default": "default_crypto",
        },
        "key_providers": {
            "section": "key_providers",
            "items": "providers",
            "default": "default_provider",
        },
    }

    def __init__(self, cfg: Dict[str, Any]) -> None:
        plugins_cfg = cfg.get("plugins", {})
        mode = plugins_cfg.get("mode", "fan-out")
        switch_map = plugins_cfg.get("switch", {})
        discover_and_register_plugins(mode=mode, switch_map=switch_map)
        self.cfg = cfg

    # ────────────────────────────── helpers ─────────────────────────────
    def _resolve_spec(self, group: str, ref: str) -> Any:
        obj = registry.get(group, {}).get(ref)
        if obj is None:
            raise InvalidPluginSpecError(ref)
        return obj

    def _instantiate(self, cls_or_obj: Any, params: Dict[str, Any]) -> Any:
        return cls_or_obj(**params) if isinstance(cls_or_obj, type) else cls_or_obj

    def _layout(self, group: str) -> Dict[str, Optional[str]]:
        return self.GROUP_CONFIG.get(
            group, {"section": group, "items": "plugins", "default": "default"}
        )

    def _group_cfg(self, group: str) -> Dict[str, Any]:
        info = self._layout(group)
        return self.cfg.get(info["section"], {})

    # ─────────────────────────────── public ──────────────────────────────
    def get(self, group: str, name: Optional[str] = None) -> Any:
        """Return a single plugin instance from ``group``."""

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
            from peagen.core._llm import GenericLLM

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

        if "single" in layout:
            ref = name or cfg.get(layout["single"])
            if not ref:
                raise KeyError(f"No plugin configured for group '{group}'")
            params = cfg.get(f"{layout['single']}_params", {})
            return self._instantiate(self._resolve_spec(group, ref), params)

        items = cfg.get(layout.get("items", "plugins"), {})
        if name is None:
            default_key = layout.get("default")
            if default_key and default_key in cfg:
                name = cfg.get(default_key)
                if name is None:
                    return None
            else:
                name = cfg.get(default_key) if default_key else None
        if not name:
            raise KeyError(f"No plugin name provided for group '{group}'")
        params = items.get(name, {})
        return self._instantiate(self._resolve_spec(group, name), params)

    def all(self, group: str) -> Dict[str, Any]:
        """Instantiate every configured plugin for ``group``."""

        layout = self._layout(group)
        cfg = self._group_cfg(group)

        if "single" in layout:
            ref = cfg.get(layout["single"])
            if not ref:
                return {}
            params = cfg.get(f"{layout['single']}_params", {})
            return {ref: self._instantiate(self._resolve_spec(group, ref), params)}

        items = cfg.get(layout.get("items", "plugins"), {})
        out: Dict[str, Any] = {}
        for name, params in items.items():
            out[name] = self._instantiate(self._resolve_spec(group, name), params)
        return out


__all__ = [
    "registry",
    "discover_and_register_plugins",
    "PluginManager",
]
