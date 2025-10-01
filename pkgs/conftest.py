from __future__ import annotations

from pathlib import Path

import pytest


def _should_load_griffe_plugin() -> bool:
    plugin_root = (Path(__file__).resolve().parent / "community" / "swarmauri_tests_griffe").resolve()
    try:
        cwd = Path.cwd().resolve()
    except FileNotFoundError:
        # Fall back to loading the plugin if the current working directory was removed.
        return True
    return plugin_root not in {cwd, *cwd.parents}


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
