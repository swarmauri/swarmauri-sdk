import pytest

from tigrbl import Base, TigrblApi, TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String


class Zeta(Base, GUIDPk):
    __tablename__ = "zeta_api_app_decl"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class ZetaApi(TigrblApi):
    MODELS = (Zeta,)


class ZetaApp(TigrblApp):
    APIS = (ZetaApi,)


@pytest.mark.unit
def test_tigrbl_api_app_subclass_declares_composition() -> None:
    api_dir = dir(ZetaApi)
    app_dir = dir(ZetaApp)

    assert "MODELS" in api_dir
    assert "APIS" in app_dir
    assert ZetaApi.MODELS == (Zeta,)
    assert ZetaApp.APIS == (ZetaApi,)
