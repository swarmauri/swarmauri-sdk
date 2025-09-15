from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Dict

import pytest
from importlib.metadata import PackageNotFoundError, distribution
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib  # type: ignore

PLUGIN_NAME = __name__.split(".")[0]


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register command-line options for license scanning."""
    group = parser.getgroup("pylicense")
    group.addoption(
        "--pylicense-mode",
        action="store",
        default="parameterized",
        choices=["parameterized", "aggregate"],
        help="Report licenses per dependency or as a single aggregate test.",
    )
    group.addoption(
        "--pylicense-package",
        action="store",
        default=None,
        help="Package name to inspect (defaults to project name in pyproject.toml).",
    )


def _default_package(config: pytest.Config) -> str:
    pkg = config.getoption("--pylicense-package")
    if pkg:
        return pkg
    inifile = getattr(config, "inifile", None)
    if inifile and Path(inifile).suffix == ".toml":
        data = tomllib.loads(Path(inifile).read_text())
        project = data.get("project") or {}
        name = project.get("name")
        if name:
            return str(name)
    raise pytest.UsageError(
        "Could not determine package name; use --pylicense-package."
    )


def _collect_licenses(pkg: str) -> Dict[str, str]:
    """Return mapping of dependency names to their licenses."""
    licenses: Dict[str, str] = {}
    queue: deque[str] = deque([pkg])
    while queue:
        name = queue.popleft()
        canon = canonicalize_name(name)
        if canon in licenses:
            continue
        try:
            dist = distribution(name)
        except PackageNotFoundError:
            licenses[canon] = "UNKNOWN"
            continue
        meta = dist.metadata
        license_str = meta.get("License", "").strip()
        if not license_str or license_str == "UNKNOWN":
            classifiers = [
                c for c in meta.get_all("Classifier", []) if c.startswith("License ::")
            ]
            if classifiers:
                license_str = " / ".join(c.split("::")[-1].strip() for c in classifiers)
            else:
                license_str = "UNKNOWN"
        licenses[canon] = license_str
        for req in dist.requires or []:
            queue.append(Requirement(req).name)
    return licenses


class LicenseItem(pytest.Item):
    def __init__(self, name: str, parent: pytest.Collector, dep: str, license: str):
        super().__init__(name, parent)
        self.dep = dep
        self.license = license

    def runtest(self) -> None:  # pragma: no cover - simple assertion
        if self.license == "UNKNOWN":
            raise AssertionError(f"{self.dep} has unknown license")

    def reportinfo(self) -> tuple[Path, None, str]:
        return Path(self.dep), None, f"license check for {self.dep}"


class LicenseAggregateItem(pytest.Item):
    def __init__(self, name: str, parent: pytest.Collector, licenses: Dict[str, str]):
        super().__init__(name, parent)
        self.licenses = licenses

    def runtest(self) -> None:  # pragma: no cover - simple aggregation
        failures = [
            f"{dep} has unknown license"
            for dep, lic in self.licenses.items()
            if lic == "UNKNOWN"
        ]
        if failures:
            pytest.fail("\n".join(failures))

    def reportinfo(self) -> tuple[str, None, str]:
        return "license aggregate", None, "license aggregate check"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "pylicense: dependency license checks")
    pkg = _default_package(config)
    config._pylicense_licenses = _collect_licenses(pkg)


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    if getattr(config, "_pylicense_items_added", False):
        return
    config._pylicense_items_added = True
    licenses: Dict[str, str] = config._pylicense_licenses
    mode: str = config.getoption("--pylicense-mode")
    if mode == "parameterized":
        for dep, lic in sorted(licenses.items()):
            item = LicenseItem.from_parent(
                session,
                name=f"{PLUGIN_NAME}:license::{dep}",
                dep=dep,
                license=lic,
            )
            items.append(item)
    else:
        item = LicenseAggregateItem.from_parent(
            session,
            name=f"{PLUGIN_NAME}:license-aggregate",
            licenses=licenses,
        )
        items.append(item)


__all__ = ["_collect_licenses"]
