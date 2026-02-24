from __future__ import annotations

from tigrbl.app.mro_collect import mro_collect_app_spec
from tigrbl.app.shortcuts import deriveApp


def test_derive_app_spec_values() -> None:
    AppCls = deriveApp(title="Example", version="2.0")
    spec = mro_collect_app_spec(AppCls)
    assert spec.title == "Example"
    assert spec.version == "2.0"
