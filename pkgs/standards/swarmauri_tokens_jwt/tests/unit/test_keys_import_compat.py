from __future__ import annotations

import importlib

from swarmauri_core.key_providers import IKeyProvider, KeyAlg


def test_legacy_keys_module_imports() -> None:
    keys_module = importlib.import_module("swarmauri_core.keys")

    assert keys_module.IKeyProvider is IKeyProvider
    assert keys_module.KeyAlg is KeyAlg
