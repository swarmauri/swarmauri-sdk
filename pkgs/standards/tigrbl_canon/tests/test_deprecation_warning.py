from __future__ import annotations

import importlib
import sys

import pytest


def _clear_tigrbl_canon_modules() -> None:
    to_remove = [
        name
        for name in sys.modules
        if name == "tigrbl_canon" or name.startswith("tigrbl_canon.")
    ]
    for name in to_remove:
        sys.modules.pop(name, None)


def test_import_tigrbl_canon_emits_deprecation_warning() -> None:
    _clear_tigrbl_canon_modules()

    with pytest.deprecated_call(match="tigrbl_canon is deprecated"):
        importlib.import_module("tigrbl_canon")


def test_import_tigrbl_canon_mapping_emits_deprecation_warning() -> None:
    _clear_tigrbl_canon_modules()

    with pytest.deprecated_call(match="tigrbl_canon is deprecated"):
        importlib.import_module("tigrbl_canon.mapping")
