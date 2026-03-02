from __future__ import annotations

from tigrbl.mapping.app_mro_collect import mro_collect_app_spec
from tigrbl.shortcuts.app import defineAppSpec


def test_app_mro_precedence() -> None:
    class BaseSpec(defineAppSpec(title="TableBase", version="1.0", routers=("base",))):
        pass

    class OverrideSpec(
        defineAppSpec(title="Override", version="2.0", routers=("extra",))
    ):
        pass

    class AppCls(OverrideSpec, BaseSpec):
        pass

    spec = mro_collect_app_spec(AppCls)
    assert spec.title == "Override"
    assert spec.routers == ("base", "base", "extra", "extra", "extra")
