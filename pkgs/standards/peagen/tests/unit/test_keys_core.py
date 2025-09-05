"""Tests for :mod:`peagen.core.keys_core`.

These exercises the plugin resolution path used by ``create_keypair``.
"""

from __future__ import annotations

from pathlib import Path

from peagen.core import keys_core


class DummyRef:
    """Simple container mimicking a key reference returned by a provider."""

    material = b"priv"
    public = b"pub"
    tags = {"ssh_fingerprint": "FP"}


class DummyDriver:
    """Minimal key provider used for testing."""

    def __init__(self, key_dir: Path) -> None:
        self.key_dir = key_dir
        self.create_called = False

    async def create_key(self, spec):  # pragma: no cover - spec unused
        self.create_called = True
        return DummyRef()

    async def import_key(self, spec, material, public):  # pragma: no cover
        return DummyRef()


class DummyPM:
    """Stand-in plugin manager returning our dummy driver."""

    def __init__(self, key_dir: Path) -> None:
        self.key_dir = key_dir
        self.called = False

    def get(self, group: str, name: str | None = None):
        assert group == "key_providers"
        self.called = True
        return DummyDriver(self.key_dir)


def test_create_keypair_uses_plugin_manager(monkeypatch, tmp_path: Path) -> None:
    """``create_keypair`` should resolve providers via ``PluginManager``."""

    monkeypatch.setattr(keys_core, "resolve_cfg", lambda: {})
    pm = DummyPM(tmp_path)
    monkeypatch.setattr(keys_core, "PluginManager", lambda cfg: pm)

    out = keys_core.create_keypair(key_dir=tmp_path)

    assert pm.called
    assert out["fingerprint"] == "FP"
    assert out["public_key"] == "pub"
    assert (tmp_path / "ssh-private").read_text() == "priv"
    assert (tmp_path / "ssh-public").read_text() == "pub"
