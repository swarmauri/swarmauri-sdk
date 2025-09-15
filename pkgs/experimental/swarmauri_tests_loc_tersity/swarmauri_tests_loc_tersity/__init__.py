from __future__ import annotations

from pathlib import Path

import pytest

DEFAULT_MAX_LINES = 400
PLUGIN_NAME = "swarmauri_tests_loc_tersity"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register command-line options for LOC testing."""
    group = parser.getgroup("loc")
    group.addoption(
        "--loc-mode",
        action="store",
        default="parameterized",
        choices=["parameterized", "aggregate"],
        help="Run LOC checks per file or as a single aggregate test.",
    )
    group.addoption(
        "--loc-root",
        action="store",
        default=None,
        help="Root directory to scan for .py files (defaults to package root).",
    )
    group.addoption(
        "--loc-max-lines",
        action="store",
        type=int,
        default=DEFAULT_MAX_LINES,
        help="Maximum allowed lines per file.",
    )


def _collect_files(config: pytest.Config) -> tuple[Path, list[Path]]:
    root = config.getoption("--loc-root")
    base = Path(root).resolve() if root else Path(config.rootpath)
    files = sorted(p for p in base.rglob("*.py") if p.is_file())
    return base, files


class LocItem(pytest.Item):
    def __init__(self, name: str, parent: pytest.Collector, path: Path, max_lines: int):
        super().__init__(name, parent)
        self.path = path
        self.max_lines = max_lines

    def runtest(self) -> None:
        count = sum(1 for _ in self.path.open())
        if count > self.max_lines:
            raise AssertionError(f"{self.path} has {count} lines (>{self.max_lines})")

    def reportinfo(self) -> tuple[Path, None, str]:
        return self.path, None, f"loc check for {self.path.name}"


class LocAggregateItem(pytest.Item):
    def __init__(
        self, name: str, parent: pytest.Collector, files: list[Path], max_lines: int
    ):
        super().__init__(name, parent)
        self.files = files
        self.max_lines = max_lines

    def runtest(self) -> None:
        failures = []
        for file in self.files:
            count = sum(1 for _ in file.open())
            if count > self.max_lines:
                failures.append(f"{file} has {count} lines (>{self.max_lines})")
        if failures:
            pytest.fail("\n".join(failures))

    def reportinfo(self) -> tuple[str, None, str]:
        return "loc aggregate", None, "loc aggregate check"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "loc: line count checks")
    base, files = _collect_files(config)
    config._loc_base = base
    config._loc_files = files


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    if getattr(config, "_loc_items_added", False):
        return
    config._loc_items_added = True
    base: Path = config._loc_base
    files: list[Path] = config._loc_files
    max_lines: int = config.getoption("--loc-max-lines")
    mode: str = config.getoption("--loc-mode")
    if mode == "parameterized":
        for file in files:
            rel = file.relative_to(base)
            item = LocItem.from_parent(
                session,
                name=f"{PLUGIN_NAME}:loc::{rel}",
                path=file,
                max_lines=max_lines,
            )
            items.append(item)
    else:
        item = LocAggregateItem.from_parent(
            session,
            name=f"{PLUGIN_NAME}:loc-aggregate",
            files=files,
            max_lines=max_lines,
        )
        items.append(item)
