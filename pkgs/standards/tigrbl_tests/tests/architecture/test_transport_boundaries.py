from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl"


def test_transport_boundary_removed_modules_absent() -> None:
    transport = ROOT / "transport"
    removed = {
        "contracts.py",
        "dispatch.py",
        "dispatcher.py",
        "gateway.py",
        "gw.py",
        "headers.py",
        "httpx.py",
        "request.py",
        "request_adapters.py",
        "response.py",
    }
    assert all(not (transport / name).exists() for name in removed)
