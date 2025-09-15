from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

import os
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
    group.addoption(
        "--pylicense-allow-list",
        action="store",
        default=None,
        help="Comma-separated list of allowed license names.",
    )
    group.addoption(
        "--pylicense-disallow-list",
        action="store",
        default=None,
        help="Comma-separated list of forbidden license names.",
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


@dataclass
class PackageLicense:
    license: str
    version: str


@dataclass
class DependencyPath:
    path: Tuple[str, ...]
    license: str
    version: str


def _license_from_metadata(meta) -> str:
    license_str = meta.get("License", "").strip()
    if not license_str or license_str == "UNKNOWN":
        classifiers = [
            c for c in meta.get_all("Classifier", []) if c.startswith("License ::")
        ]
        if classifiers:
            license_str = " / ".join(c.split("::")[-1].strip() for c in classifiers)
        else:
            license_str = "UNKNOWN"
    return license_str


def _collect_dependency_paths(pkg: str) -> List[DependencyPath]:
    paths: List[DependencyPath] = []
    queue: deque[Tuple[str, Tuple[str, ...]]] = deque([(pkg, (pkg,))])
    seen: Set[str] = set()
    while queue:
        name, path = queue.popleft()
        canon = canonicalize_name(name)
        if canon in seen:
            continue
        seen.add(canon)
        try:
            dist = distribution(name)
        except PackageNotFoundError:
            lic = "UNKNOWN"
            ver = "UNKNOWN"
            dist = None
        else:
            lic = _license_from_metadata(dist.metadata)
            ver = dist.version
        if len(path) > 1:
            paths.append(DependencyPath(path, lic, ver))
        if dist:
            for req in dist.requires or []:
                dep_name = Requirement(req).name
                queue.append((dep_name, path + (dep_name,)))
    return paths


def _collect_licenses(pkg: str) -> Dict[str, PackageLicense]:
    paths = _collect_dependency_paths(pkg)
    return {
        canonicalize_name(p.path[-1]): PackageLicense(p.license, p.version)
        for p in paths
    }


class LicenseItem(pytest.Item):
    def __init__(
        self,
        name: str,
        parent: pytest.Collector,
        dep: str,
        version: str,
        license: str,
    ):
        super().__init__(name, parent)
        self.dep = dep
        self.version = version
        self.license = license

    def runtest(self) -> None:  # pragma: no cover - simple assertion
        allow: Set[str] = getattr(self.config, "_pylicense_allow", set())
        disallow: Set[str] = getattr(self.config, "_pylicense_disallow", set())
        lic = self.license
        if lic == "UNKNOWN":
            pytest.fail(
                f"{self.dep}=={self.version} has unknown license", pytrace=False
            )
        if disallow and lic in disallow:
            pytest.fail(
                f"{self.dep}=={self.version} uses forbidden license {lic}",
                pytrace=False,
            )
        if allow and lic not in allow:
            pytest.fail(
                f"{self.dep}=={self.version} has disallowed license {lic}",
                pytrace=False,
            )

    def reportinfo(self) -> tuple[Path, None, str]:
        return (
            Path.cwd(),
            None,
            f"license check for {self.dep}=={self.version} [{self.license}]",
        )


class LicenseAggregateItem(pytest.Item):
    def __init__(
        self, name: str, parent: pytest.Collector, licenses: Dict[str, PackageLicense]
    ):
        super().__init__(name, parent)
        self.licenses = licenses

    def runtest(self) -> None:  # pragma: no cover - simple aggregation
        allow: Set[str] = getattr(self.config, "_pylicense_allow", set())
        disallow: Set[str] = getattr(self.config, "_pylicense_disallow", set())
        failures = []
        for dep, info in self.licenses.items():
            lic = info.license
            ver = info.version
            if lic == "UNKNOWN":
                failures.append(f"{dep}=={ver} has unknown license")
            elif disallow and lic in disallow:
                failures.append(f"{dep}=={ver} uses forbidden license {lic}")
            elif allow and lic not in allow:
                failures.append(f"{dep}=={ver} has disallowed license {lic}")
        if failures:
            pytest.fail("\n".join(failures))

    def reportinfo(self) -> tuple[Path, None, str]:
        pkg = getattr(self.config, "_pylicense_pkg", "package")
        return Path.cwd(), None, f"license aggregate check for {pkg}"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "pylicense: dependency license checks")
    pkg = _default_package(config)
    config._pylicense_pkg = pkg
    paths = _collect_dependency_paths(pkg)
    config._pylicense_paths = paths
    config._pylicense_licenses = {
        canonicalize_name(p.path[-1]): PackageLicense(p.license, p.version)
        for p in paths
    }
    allow = _parse_list(
        config.getoption("--pylicense-allow-list"), "PYLICENSE_ALLOW_LIST"
    )
    disallow = _parse_list(
        config.getoption("--pylicense-disallow-list"), "PYLICENSE_DISALLOW_LIST"
    )
    config._pylicense_allow = allow
    config._pylicense_disallow = disallow


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    if getattr(config, "_pylicense_items_added", False):
        return
    config._pylicense_items_added = True
    mode: str = config.getoption("--pylicense-mode")
    if mode == "parameterized":
        paths: List[DependencyPath] = config._pylicense_paths
        for dp in sorted(paths, key=lambda p: p.path):
            path_str = "::".join(dp.path)
            item = LicenseItem.from_parent(
                session,
                name=f"{PLUGIN_NAME}:license::{path_str}=={dp.version} [{dp.license}]",
                dep=dp.path[-1],
                version=dp.version,
                license=dp.license,
            )
            items.append(item)
    else:
        item = LicenseAggregateItem.from_parent(
            session,
            name=f"{PLUGIN_NAME}:license-aggregate::{config._pylicense_pkg}",
            licenses=config._pylicense_licenses,
        )
        items.append(item)


def _parse_list(value: str | None, env: str) -> Set[str]:
    val = value or os.getenv(env)
    if not val:
        return set()
    return {v.strip() for v in val.split(",") if v.strip()}


__all__ = [
    "_collect_licenses",
    "_collect_dependency_paths",
    "PackageLicense",
    "DependencyPath",
]
