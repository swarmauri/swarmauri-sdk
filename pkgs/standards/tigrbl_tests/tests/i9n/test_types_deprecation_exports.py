from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import pytest

import tigrbl.types as types_module


_DEPRECATED_NAMES = {
    "Router": "tigrbl.router",
    "Request": "tigrbl.requests",
    "Body": "tigrbl.core.crud",
    "Depends": "tigrbl.security",
    "HTTPException": "tigrbl.runtime.status",
    "Response": "tigrbl.responses",
}


def _major_minor(v: str) -> tuple[int, int]:
    clean = v.split(".dev", 1)[0]
    parts = clean.split(".")
    return int(parts[0]), int(parts[1])


@pytest.mark.i9n
def test_types_deprecated_exports_only_exist_before_next_minor():
    src = Path(types_module.__file__).read_text(encoding="utf-8")
    current_major_minor = _major_minor(version("tigrbl"))

    if current_major_minor >= (0, 4):
        assert "no longer exports" not in src
        for name in _DEPRECATED_NAMES:
            assert f'"{name}"' not in src
        return

    assert "no longer exports" in src

    for name, module in _DEPRECATED_NAMES.items():
        with pytest.raises(AttributeError) as exc:
            getattr(types_module, name)
        assert "no longer exports" in str(exc.value)
        assert f"Import it from '{module}' instead." in str(exc.value)
