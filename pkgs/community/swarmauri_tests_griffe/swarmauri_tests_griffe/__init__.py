"""Pytest plugin for detecting Griffe warnings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import importlib
import warnings

import pytest

try:  # pragma: no cover - optional dependency resolution
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

import griffe

PLUGIN_NAME = "swarmauri_tests_griffe"


@dataclass(frozen=True)
class GriffeTarget:
    """Representation of a package that should be inspected by Griffe."""

    name: str
    path: Path

    @property
    def search_path(self) -> Path:
        return self.path.parent


def pytest_addoption(parser: pytest.Parser) -> None:
    """Expose configuration options for the plugin."""

    group = parser.getgroup("griffe")
    group.addoption(
        "--griffe-package",
        action="append",
        dest="griffe_packages",
        default=None,
        help=(
            "Package name to inspect with Griffe. "
            "Can be provided multiple times. Defaults to the package defined in pyproject.toml."
        ),
    )
    group.addoption(
        "--griffe-root",
        action="store",
        dest="griffe_root",
        default=None,
        help="Root directory for resolving packages (defaults to pytest's rootpath).",
    )


def _normalized(name: str) -> str:
    return name.replace("-", "_")


def _candidate_paths(root: Path, name: str) -> list[Path]:
    candidates = [root / name, root / "src" / name]
    return [path for path in candidates if path.exists()]


def _discover_from_pyproject(root: Path) -> list[str]:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return []
    try:
        data = tomllib.loads(pyproject.read_text())
    except (
        Exception
    ):  # pragma: no cover - toml parsing errors should not crash test runs
        return []
    project = data.get("project", {})
    name = project.get("name")
    if not name:
        return []
    return [_normalized(name)]


def _discover_packages(config: pytest.Config) -> list[GriffeTarget]:
    root_option = config.getoption("griffe_root")
    root = Path(root_option).resolve() if root_option else Path(config.rootpath)
    packages = config.getoption("griffe_packages")
    explicit = bool(packages)
    package_names: list[str]
    if packages:
        package_names = [_normalized(name) for name in packages]
    else:
        package_names = _discover_from_pyproject(root)
        if not package_names:
            package_names = sorted(
                path.name
                for path in root.iterdir()
                if path.is_dir()
                and not path.name.startswith(".")
                and path.name not in {"tests", "__pycache__"}
                and (path / "__init__.py").exists()
            )
    targets: list[GriffeTarget] = []
    seen: set[str] = set()
    for package in package_names:
        if package in seen:
            continue
        for candidate in _candidate_paths(root, package):
            if (candidate / "__init__.py").exists():
                targets.append(GriffeTarget(name=package, path=candidate))
                seen.add(package)
                break
        else:
            # Fall back to importing the module to resolve its path.
            try:
                module = importlib.import_module(package)
            except (
                Exception
            ):  # pragma: no cover - import failure should surface during test discovery
                if explicit:
                    raise pytest.UsageError(
                        f"Unable to resolve package '{package}' for Griffe inspection."
                    ) from None
                continue
            module_file = getattr(module, "__file__", None)
            if not module_file:
                if explicit:
                    raise pytest.UsageError(
                        f"Unable to resolve package '{package}' for Griffe inspection."
                    )
                continue
            targets.append(
                GriffeTarget(name=package, path=Path(module_file).resolve().parent)
            )
            seen.add(package)
    return targets


class GriffeWarningsItem(pytest.Item):
    """Pytest item responsible for executing the Griffe warning checks."""

    def __init__(
        self,
        name: str,
        parent: pytest.Collector,
        target: GriffeTarget,
    ) -> None:
        super().__init__(name, parent)
        self.target = target
        self.add_marker("griffe")

    def runtest(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            griffe.load(self.target.name, search_paths=[str(self.target.search_path)])
        griffe_warnings = [
            warning
            for warning in caught
            if "griffe" in (warning.filename or "")
            or warning.category.__module__.startswith("griffe")
        ]
        # If we didn't detect explicit Griffe warnings but still captured warnings,
        # treat them as relevant—Griffe ran and triggered them during inspection.
        relevant = griffe_warnings or caught
        if relevant:
            formatted = "\n".join(
                f"{warning.category.__name__}: {warning.message} ({warning.filename}:{warning.lineno})"
                for warning in relevant
            )
            raise AssertionError(
                f"Griffe emitted warnings while loading {self.target.name}:\n{formatted}"
            )

    def reportinfo(self) -> tuple[Path, int | None, str]:
        return self.target.path, None, f"griffe warnings for {self.target.name}"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "griffe: validate packages with griffe")
    targets = _discover_packages(config)
    config._swarmauri_griffe_targets = targets


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    targets: list[GriffeTarget] = getattr(config, "_swarmauri_griffe_targets", [])
    if not targets:
        return
    for target in targets:
        item = GriffeWarningsItem.from_parent(
            session,
            name=f"{PLUGIN_NAME}::{target.name}",
            target=target,
        )
        items.append(item)


__all__ = [
    "GriffeWarningsItem",
    "GriffeTarget",
    "PLUGIN_NAME",
]
