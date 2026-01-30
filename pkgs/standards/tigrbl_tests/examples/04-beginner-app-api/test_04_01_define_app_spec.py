from __future__ import annotations

from tigrbl.app.mro_collect import mro_collect_app_spec
from tigrbl.app.shortcuts import defineAppSpec


def test_define_app_spec_values() -> None:
    class BaseSpec(defineAppSpec(title="Acme", version="1.0")):
        pass

    spec = mro_collect_app_spec(BaseSpec)
    assert spec.title == "Acme"
    assert spec.version == "1.0"
