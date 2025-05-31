from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List

from peagen.plugin_registry import registry


class TemplateManager:
    """Manage Jinja template search paths."""

    def __init__(
        self,
        j2pt: Any,
        cwd: str,
        workspace_root: Path | None,
        source_packages: List[Dict[str, Any]],
        logger,
    ) -> None:
        self.j2pt = j2pt
        self.cwd = cwd
        self.workspace_root = workspace_root
        self.source_packages = source_packages
        self.logger = logger
        self.namespace_dirs: List[str] = []
        self._setup_env()

    def _setup_env(self) -> None:
        """Populate ``namespace_dirs`` and reset Jinja search paths."""
        ns_dirs: List[str] = []
        for plugin in registry.get("template_sets", {}).values():
            pkg: ModuleType = (
                plugin if isinstance(plugin, ModuleType) else import_module(plugin.__module__.split(".", 1)[0])
            )
            if hasattr(pkg, "__path__"):
                ns_dirs.extend(str(p) for p in pkg.__path__)

        if self.workspace_root is not None:
            ns_dirs.insert(0, os.fspath(self.workspace_root))

        for spec in self.source_packages:
            if spec.get("expose_to_jinja"):
                ns_dirs.append(os.fspath(Path(self.workspace_root or ".") / spec["dest"]))

        ns_dirs.append(self.cwd)

        self.namespace_dirs = ns_dirs
        self.j2pt.templates_dir = []

    def update_templates_dir(self, package_specific_template_dir: str | Path) -> None:
        """Update Jinja search path for a package-specific render call."""
        dirs = [
            os.fspath(package_specific_template_dir),
            self.cwd,
            *[
                os.fspath(Path(self.workspace_root or ".") / spec["dest"])
                for spec in self.source_packages
                if spec.get("expose_to_jinja")
            ],
        ]
        self.logger.debug(
            f"Updated from {self.j2pt.templates_dir} to {[os.path.normpath(d) for d in dirs]}"
        )
        self.j2pt.templates_dir = [os.path.normpath(d) for d in dirs]

    def locate_template_set(self, template_set: str) -> Path:
        """Search ``namespace_dirs`` for the given template-set folder."""
        self.logger.debug(f"locating template-set: {template_set}")
        if template_set in registry["template_sets"]:
            self.logger.debug(list(registry["template_sets"][template_set].__path__)[0])
            return list(registry["template_sets"][template_set].__path__)[0]
        raise ValueError(f"Template set '{template_set}' not found in: {self.namespace_dirs}")
