from tigrbl.app.mro_collect import mro_collect_app_spec
from tigrbl.app.shortcuts import defineAppSpec, deriveApp


class BaseAppSpec(defineAppSpec(title="Base", version="1.0", apis=("base",))):
    pass


class ChildApp(BaseAppSpec):
    APIS = ("child",)
    OPS = ("read",)


def test_app_spec_defaults_and_merge():
    spec = mro_collect_app_spec(ChildApp)
    assert spec.title == "Base"
    assert spec.version == "1.0"
    assert spec.apis == ("child", "base")
    assert spec.ops == ("read",)
    assert spec.models == ()
    assert spec.schemas == ()
    assert spec.hooks == ()


def test_app_spec_shortcut_derivation():
    Derived = deriveApp(title="Svc", version="2.0")
    assert Derived.TITLE == "Svc"
    assert Derived.VERSION == "2.0"
