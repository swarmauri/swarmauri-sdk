from __future__ import annotations

from pathlib import Path

import tigrbl


def test_transport_modules_do_not_execute_security_dependencies() -> None:
    root = Path(tigrbl.__file__).resolve().parent
    targets = [
        root / "transport" / "dispatcher.py",
        root / "bindings" / "rest" / "router.py",
        root / "bindings" / "rest" / "routing.py",
    ]
    forbidden = (
        "_require_auth_header",
        "_requires_auth_header",
        "Security(",
        "HTTPBearer(",
        "authorization",
    )
    for path in targets:
        text = path.read_text()
        for token in forbidden:
            assert token not in text, f"{token!r} found in {path}"
