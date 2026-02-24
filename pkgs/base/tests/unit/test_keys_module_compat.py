from __future__ import annotations

import importlib

from swarmauri_core.key_providers import KeyAlg


def test_core_keys_module_available() -> None:
    keys_module = importlib.import_module("swarmauri_core.keys")

    assert keys_module.KeyAlg is KeyAlg
