import pytest

from tigrbl import Base, TigrblApi, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String


class Theta(Base, GUIDPk):
    __tablename__ = "theta_api_app_inst"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class ThetaApi(TigrblApi):
    MODELS = (Theta,)


@pytest.mark.unit
def test_tigrbl_api_app_instantiation_sets_composed_state() -> None:
    api = ThetaApi(engine=mem(async_=False))

    class ThetaApp(TigrblApp):
        APIS = (api,)

    app = ThetaApp(engine=mem(async_=False))

    api_dir = dir(api)
    app_dir = dir(app)

    assert "models" in api_dir
    assert api.models["Theta"] is Theta
    assert "apis" in app_dir
    assert app.apis == [api]
