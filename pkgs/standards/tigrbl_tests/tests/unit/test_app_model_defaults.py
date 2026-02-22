from tigrbl.app.shortcuts import deriveApp
from tigrbl.router.shortcuts import deriveRouter


class Model:
    __tablename__ = "model"


def test_derive_app_prefills_model_registry() -> None:
    AppCls = deriveApp(models=[Model])
    app = AppCls()
    assert app.models["Model"] is Model


def test_derive_router_prefills_model_registry() -> None:
    ApiCls = deriveRouter(tables=[Model])
    api = ApiCls()
    assert api.models["Model"] is Model


def test_registry_includes_alias_and_name() -> None:
    class AliasModel:
        __tablename__ = "alias_model"

    ApiCls = deriveRouter(tables=[AliasModel])
    api = ApiCls()
    assert api.models["AliasModel"] is AliasModel
