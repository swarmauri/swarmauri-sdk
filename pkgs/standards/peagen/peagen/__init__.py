"""Initialize the Peagen package and register plugins."""

import sys as _sys
from .plugin_registry import discover_and_register_plugins


def _determine_plugin_mode() -> str:
    """Resolve plugin loading mode from CLI flags or ``.peagen.toml``."""
    args = _sys.argv[1:]
    for i, arg in enumerate(args):
        if arg.startswith("--plugin-mode="):
            return arg.split("=", 1)[1]
        if arg in {"--plugin-mode", "--plugin_mode"} and i + 1 < len(args):
            return args[i + 1]

    try:
        from peagen.cli_common import load_peagen_toml

        cfg = load_peagen_toml()
        mode = cfg.get("peagen", {}).get("plugin_mode")
        if mode:
            return mode
    except Exception:
        pass

    return "fan-out"


discover_and_register_plugins(mode=_determine_plugin_mode())
