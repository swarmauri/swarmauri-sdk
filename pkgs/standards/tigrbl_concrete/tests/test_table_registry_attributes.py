import pytest

from tigrbl_concrete._concrete.tigrbl_app import TigrblApp
from tigrbl_concrete._concrete.tigrbl_router import TigrblRouter


@pytest.mark.unit
def test_app_exposes_table_registry_attribute() -> None:
    app = TigrblApp()

    assert hasattr(app, "_table_registry")


@pytest.mark.unit
def test_router_exposes_table_regsitry_attribute() -> None:
    router = TigrblRouter()

    assert hasattr(router, "_table_regsitry")
