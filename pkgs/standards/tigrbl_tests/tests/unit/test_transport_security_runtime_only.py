from __future__ import annotations

from pathlib import Path

import tigrbl_concrete


def test_transport_modules_do_not_execute_security_dependencies() -> None:
    """REST transport/routing modules must not hard-code security logic.

    Security is injected via dependency objects at runtime, not baked
    into the router/routing source files.
    """
    root = Path(tigrbl_concrete.__file__).resolve().parent
    targets = [
        root / "_mapping" / "router" / "common.py",
        root / "_mapping" / "router" / "rpc.py",
    ]
    forbidden = (
        "_require_auth_header",
        "_requires_auth_header",
        "Security(",
        "HTTPBearer(",
        "security_dependencies",
    )
    for path in targets:
        text = path.read_text()
        for token in forbidden:
            assert token not in text, f"{token!r} found in {path}"
