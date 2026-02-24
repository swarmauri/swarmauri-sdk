from __future__ import annotations

import swarmauri_core.keys as keys
from swarmauri_core.key_providers import (
    ExportPolicy,
    IKeyProvider,
    KeyAlg,
    KeyClass,
    KeyRef,
    KeySpec,
    KeyUse,
)


def test_keys_module_exports_match_key_providers() -> None:
    assert keys.IKeyProvider is IKeyProvider
    assert keys.KeyAlg is KeyAlg
    assert keys.KeyClass is KeyClass
    assert keys.KeySpec is KeySpec
    assert keys.ExportPolicy is ExportPolicy
    assert keys.KeyUse is KeyUse
    assert keys.KeyRef is KeyRef
