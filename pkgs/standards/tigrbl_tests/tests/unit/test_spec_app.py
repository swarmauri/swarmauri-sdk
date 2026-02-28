from tigrbl._spec.app_spec import AppSpec
from tigrbl._concrete._app import App
from tigrbl.shortcuts.app import defineAppSpec, deriveApp


class BaseAppSpec(defineAppSpec(title="TableBase", version="1.0", routers=("base",))):
    pass


class ChildApp(BaseAppSpec):
    ROUTERS = ("child",)
    OPS = ("read",)


def test_app_spec_defaults_and_merge():
    spec = AppSpec.collect(ChildApp)
    assert spec.title == "TableBase"
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


class BaseConcreteApp(App):
    ROUTERS = ("base_router",)
    OPS = ("base_op",)
    TABLES = ("base_table",)


class ChildConcreteApp(BaseConcreteApp):
    ROUTERS = ("child_router",)
    OPS = ("child_op",)


def test_concrete_app_initializes_from_mro_collect_spec():
    app = ChildConcreteApp()

    assert app.routers == ("child_router", "base_router")
    assert app.ops == ("child_op", "base_op")
    assert tuple(app.tables.values()) == ("base_table",)
