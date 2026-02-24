import pytest

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem


@pytest.mark.unit
def test_tigrbl_app_exposes_state_namespace() -> None:
    app = TigrblApp(engine=mem(async_=False))

    assert hasattr(app, "state")


@pytest.mark.unit
def test_tigrbl_app_state_allows_attribute_assignment() -> None:
    app = TigrblApp(engine=mem(async_=False))

    app.state.tenant = "tenant-123"

    assert app.state.tenant == "tenant-123"
