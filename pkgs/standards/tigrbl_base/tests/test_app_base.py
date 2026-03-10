import types

from tigrbl_base._base._app_base import AppBase
from tigrbl_core._spec.app_spec import AppSpec


def test_app_base_defaults() -> None:
    app = AppBase()

    assert isinstance(app, AppSpec)
    assert app.title == "Tigrbl"
    assert app.version == "0.1.0"
    assert app.jsonrpc_prefix == "/rpc"
    assert app.system_prefix == "/system"


def test_collect_spec_normalizes_and_collects(monkeypatch) -> None:
    module = types.ModuleType("tigrbl_canon.mapping.spec_normalization")

    def merge_seq_attr(app: type, attr: str, **_: object):
        return getattr(app, attr, ())

    def normalize_app_spec(spec: AppSpec) -> AppSpec:
        return spec

    module.merge_seq_attr = merge_seq_attr
    module.normalize_app_spec = normalize_app_spec
    monkeypatch.setitem(
        __import__("sys").modules, "tigrbl_canon.mapping.spec_normalization", module
    )

    class Parent:
        TITLE = "Parent"
        VERSION = "1.0.0"
        ROUTERS = ("r1",)

    class Child(Parent):
        DESCRIPTION = "desc"
        OPS = ("op1",)
        TABLES = ("table1",)
        SCHEMAS = ("schema1",)
        HOOKS = ("hook1",)
        SECURITY_DEPS = ("sec",)
        DEPS = ("dep",)
        MIDDLEWARES = ("mw",)

    spec = AppBase.collect_spec(Child)

    assert isinstance(spec, AppSpec)
    assert spec.title == "Parent"
    assert spec.description == "desc"
    assert spec.version == "1.0.0"
    assert spec.routers == ("r1",)
    assert spec.ops == ("op1",)
    assert spec.tables == ("table1",)
    assert spec.schemas == ("schema1",)
    assert spec.hooks == ("hook1",)
    assert spec.security_deps == ("sec",)
    assert spec.deps == ("dep",)
    assert spec.middlewares == ("mw",)
