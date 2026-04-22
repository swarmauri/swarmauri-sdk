"""Install this Codex plugin into the current user's Codex home."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


PLUGIN_NAME = "swarmauri-sdk-authoring"


def _codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def _copy_plugin(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".ruff_cache"),
    )


def _update_marketplace(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            marketplace = json.load(file)
    else:
        marketplace = {
            "name": "codex-home",
            "interface": {"displayName": "Codex Home"},
            "plugins": [],
        }

    marketplace.setdefault("name", "codex-home")
    marketplace.setdefault("interface", {}).setdefault("displayName", "Codex Home")
    plugins = marketplace.setdefault("plugins", [])
    entry = {
        "name": PLUGIN_NAME,
        "source": {
            "source": "local",
            "path": f"./plugins/{PLUGIN_NAME}",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Developer Tools",
    }

    for index, existing in enumerate(plugins):
        if existing.get("name") == PLUGIN_NAME:
            plugins[index] = entry
            break
    else:
        plugins.append(entry)

    with path.open("w", encoding="utf-8") as file:
        json.dump(marketplace, file, indent=2)
        file.write("\n")


def main() -> int:
    source = Path(__file__).resolve().parents[1]
    home = _codex_home()
    destination = home / "plugins" / PLUGIN_NAME
    marketplace = home / ".agents" / "plugins" / "marketplace.json"

    destination.parent.mkdir(parents=True, exist_ok=True)
    _copy_plugin(source, destination)
    _update_marketplace(marketplace)

    print(f"Installed {PLUGIN_NAME} to {destination}")
    print(f"Updated marketplace at {marketplace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
