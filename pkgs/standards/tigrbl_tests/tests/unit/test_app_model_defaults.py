from tigrbl.app.shortcuts import deriveApp
from tigrbl.router.shortcuts import deriveRouter


class Model:
    __tablename__ = "model"


def test_derive_app_prefills_model_registry() -> None:
    AppCls = deriveApp(tables=[Model])
    app = AppCls()
    assert app.tables["Model"] is Model


def test_derive_router_prefills_model_registry() -> None:
    RouterCls = deriveRouter(tables=[Model])
    router = RouterCls()
    assert router.tables["Model"] is Model


def test_registry_includes_alias_and_name() -> None:
    class AliasModel:
        __tablename__ = "alias_model"

    RouterCls = deriveRouter(tables=[AliasModel])
    router = RouterCls()
    assert router.tables["AliasModel"] is AliasModel
