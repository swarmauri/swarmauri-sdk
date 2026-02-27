from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl"


def _target_variants(name: str) -> tuple[str, ...]:
    return (name, f"{name}.py")


def test_transport_boundary_removed_modules_absent() -> None:
    transport = ROOT / "transport"
    removed = {
        "contracts",
        "dispatch",
        "dispatcher",
        "gateway",
        "gw",
        "headers",
        "httpx",
        "request",
        "request_adapters",
        "responses",
    }

    for name in removed:
        for candidate in _target_variants(name):
            assert not (transport / candidate).exists()
