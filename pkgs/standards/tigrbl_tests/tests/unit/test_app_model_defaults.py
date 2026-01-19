from tigrbl.app.shortcuts import deriveApp
from tigrbl.api.shortcuts import deriveApi


class Model:
    __tablename__ = "model"


def test_derive_app_prefills_model_registry() -> None:
    AppCls = deriveApp(models=[Model])
    app = AppCls()
    assert app.models["Model"] is Model


def test_derive_api_prefills_model_registry() -> None:
    ApiCls = deriveApi(models=[Model])
    api = ApiCls()
    assert api.models["Model"] is Model


def test_registry_includes_alias_and_name() -> None:
    class AliasModel:
        __tablename__ = "alias_model"

    ApiCls = deriveApi(models=[("Alias", AliasModel)])
    api = ApiCls()
    assert api.models["Alias"] is AliasModel
    assert api.models["AliasModel"] is AliasModel
