from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.i9n
def test_transport_dispatch_modules_removed():
    root = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl" / "transport"
    assert not (root / "dispatch.py").exists()
    assert not (root / "dispatcher.py").exists()
    assert not (root / "jsonrpc" / "dispatcher.py").exists()


@pytest.mark.i9n
def test_tigrbl_dispatch_exports_removed():
    import tigrbl

    assert not hasattr(tigrbl, "dispatch_operation")
    assert not hasattr(tigrbl, "resolve_operation")
