from pathlib import Path
from importlib import import_module
from types import ModuleType

from jinja2 import Environment, FileSystemLoader
import peagen.plugins
from swarmauri_standard.loggers.Logger import Logger

logger = Logger(name=__name__)


def _build_jinja_env(
    cfg: dict, *, workspace_root: str | Path | None = None
) -> Environment:
    """Return a Jinja2 Environment whose loader.searchpath reproduces the
    rules in the original Peagen._setup_env().
    """
    logger.warning("deprecate this - use _search_template_sets")
    ns_dirs: list[str] = []

    # 1) Template-set plugins discovered via registry
    for plugin in peagen.plugins.registry.get("template_sets", {}).values():
        pkg: ModuleType = (
            plugin
            if isinstance(plugin, ModuleType)
            else import_module(plugin.__module__.split(".", 1)[0])
        )

        if hasattr(pkg, "__path__"):
            ns_dirs.extend(str(p) for p in pkg.__path__)

    # 2) Workspace (so freshly generated files can be included)
    if workspace_root is not None:
        ns_dirs.insert(0, str(Path(workspace_root)))

    # 3) Extra template paths declared in .peagen.toml
    # We want to convert this to install people to configure required template_sets per .peagen.toml file
    # Should support local, git, pypi, or https based retrievals
    ns_dirs.extend(str(Path(p)) for p in cfg.get("template_paths", []))

    # 4) base_dir (repo root), if present
    if cfg.get("base_dir"):
        ns_dirs.append(str(Path(cfg["base_dir"])))

    # Deduplicate while preserving order and keeping only existing folders
    seen, search_paths = set(), []
    for p in ns_dirs:
        if p not in seen and Path(p).is_dir():
            search_paths.append(p)
            seen.add(p)

    if not search_paths:
        from peagen.errors import TemplateSearchPathError

        raise TemplateSearchPathError()

    return Environment(
        loader=FileSystemLoader(search_paths),
        autoescape=False,
    )
