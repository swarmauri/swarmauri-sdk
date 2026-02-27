from __future__ import annotations

from pathlib import Path


def test_legacy_transport_gateway_and_response_modules_removed() -> None:
    root = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl" / "transport"
    assert not (root / "gw.py").exists()
    assert not (root / "gateway.py").exists()
    assert not (root / "response.py").exists()
