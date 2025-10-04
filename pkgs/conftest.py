from __future__ import annotations

from importlib import util as importlib_util
from pathlib import Path

import pytest


def _should_load_griffe_plugin() -> bool:
    plugin_root = (Path(__file__).resolve().parent / "community" / "swarmauri_tests_griffe").resolve()
    try:
        cwd = Path.cwd().resolve()
    except FileNotFoundError:
        # Fall back to loading the plugin if the current working directory was removed.
        return True
    if plugin_root in {cwd, *cwd.parents}:
        return False

    # Only enable the plugin when it is importable in the current environment.  The
    # ``uv run --directory`` workflow used in CI constructs an isolated environment
    # that does not add the community packages to ``sys.path``.  Importing the
    # plugin in that situation raises ``ModuleNotFoundError`` during pytest's
    # bootstrap phase and prevents package-specific test suites from running.
    try:
        spec = importlib_util.find_spec("swarmauri_tests_griffe")
    except ModuleNotFoundError:
        return False
    return spec is not None


pytest_plugins = ["swarmauri_tests_griffe"] if _should_load_griffe_plugin() else []


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "infra: infrastructure tests requiring external services",
    )
    config.addinivalue_line(
        "markers",
        "smoke: comprehensive smoke tests against live services",
    )


def pytest_collection_modifyitems(config, items):
    markexpr = getattr(config.option, "markexpr", "")
    if markexpr and ("infra" in markexpr or "smoke" in markexpr):
        return
    skip_infra = pytest.mark.skip(reason="skip infra tests (use -m infra to run)")
    skip_smoke = pytest.mark.skip(reason="skip smoke tests (use -m smoke to run)")
    for item in items:
        if "infra" in item.keywords:
            item.add_marker(skip_infra)
        if "smoke" in item.keywords:
            item.add_marker(skip_smoke)
