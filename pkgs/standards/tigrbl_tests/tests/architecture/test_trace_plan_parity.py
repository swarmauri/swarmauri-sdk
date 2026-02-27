from __future__ import annotations

from pathlib import Path


def test_legacy_transport_dispatcher_file_absent():
    root = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl" / "transport"
    assert not (root / "dispatcher.py").exists()
