from tigrbl.app.mro_collect import mro_collect_app_spec
from tigrbl.app.shortcuts import defineAppSpec, deriveApp


class BaseAppSpec(defineAppSpec(title="Base", version="1.0", routers=("base",))):
    pass


class ChildApp(BaseAppSpec):
    ROUTERS = ("child",)
    OPS = ("read",)


def test_app_spec_defaults_and_merge():
    spec = mro_collect_app_spec(ChildApp)
    assert spec.title == "Base"
    assert spec.version == "1.0"
    assert spec.routers == ("child", "base")
    assert spec.ops == ("read",)
    assert spec.tables == ()
    assert spec.schemas == ()
    assert spec.hooks == ()


def test_app_spec_shortcut_derivation():
    Derived = deriveApp(title="Svc", version="2.0")
    assert Derived.TITLE == "Svc"
    assert Derived.VERSION == "2.0"
