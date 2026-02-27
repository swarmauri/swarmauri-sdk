from __future__ import annotations

from pathlib import Path

import pytest

from tigrbl import dispatch_operation, resolve_operation


@pytest.mark.i9n
def test_transport_dispatch_modules_removed():
    root = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl" / "transport"
    assert not (root / "dispatch.py").exists()
    assert not (root / "dispatcher.py").exists()
    assert not (root / "jsonrpc" / "dispatcher.py").exists()


@pytest.mark.i9n
def test_runtime_dispatch_fast_break_messages_are_explicit():
    with pytest.raises(RuntimeError, match="runtime-owned"):
        dispatch_operation(router=None)

    with pytest.raises(RuntimeError, match="runtime-owned"):
        resolve_operation(router=None)
