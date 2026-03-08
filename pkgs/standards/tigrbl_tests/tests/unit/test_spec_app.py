from tigrbl import App, AppBase
from tigrbl.shortcuts.app import defineAppSpec, deriveApp


class BaseAppSpec(defineAppSpec(title="TableBase", version="1.0", routers=("base",))):
    pass


class ChildApp(BaseAppSpec):
    ROUTERS = ("child",)
    OPS = ("read",)


def test_app_spec_defaults_and_merge():
    spec = AppBase.collect_spec(ChildApp)
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


class ScalarAttrsApp(App):
    ROUTERS = "router"
    OPS = "read"
    TABLES = "widgets"
    SCHEMAS = "WidgetSchema"
    HOOKS = "hook"
    SECURITY_DEPS = "security"
    DEPS = "dep"
    MIDDLEWARES = "mw"


def test_app_spec_normalizes_scalar_sequence_fields():
    spec = AppBase.collect_spec(ScalarAttrsApp)

    assert spec.routers == ("router",)
    assert spec.ops == ("read",)
    assert spec.tables == ("widgets",)
    assert spec.schemas == ("WidgetSchema",)
    assert spec.hooks == ("hook",)
    assert spec.security_deps == ("security",)
    assert spec.deps == ("dep",)
    assert spec.middlewares == ("mw",)
