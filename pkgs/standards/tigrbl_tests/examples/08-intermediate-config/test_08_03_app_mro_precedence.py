from __future__ import annotations

from tigrbl.app.mro_collect import mro_collect_app_spec
from tigrbl.app.shortcuts import defineAppSpec


def test_app_mro_precedence() -> None:
    class BaseSpec(defineAppSpec(title="Base", version="1.0", apis=("base",))):
        pass

    class OverrideSpec(defineAppSpec(title="Override", version="2.0", apis=("extra",))):
        pass

    class AppCls(OverrideSpec, BaseSpec):
        pass

    spec = mro_collect_app_spec(AppCls)
    assert spec.title == "Override"
    assert spec.apis == ("extra", "base")
