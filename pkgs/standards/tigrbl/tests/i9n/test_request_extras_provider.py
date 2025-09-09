import pytest

from tigrbl.v3 import Base
from tigrbl.v3.orm.mixins import GUIDPk
from tigrbl.v3.schema import _build_schema
from tigrbl.v3.types import Column, Field, RequestExtrasProvider, String
from tigrbl.v3.types.request_extras_provider import list_request_extras_providers


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_request_extras_provider_in_schema():
    Base.metadata.clear()

    class Widget(Base, GUIDPk, RequestExtrasProvider):
        __tablename__ = "widgets"
        name = Column(String, nullable=False)
        __tigrbl_request_extras__ = {
            "create": {"extra": (int | None, Field(None, exclude=True))}
        }

    SCreate = _build_schema(Widget, verb="create")
    SRead = _build_schema(Widget, verb="read")

    assert "extra" in SCreate.model_fields
    assert "extra" not in SRead.model_fields
    assert Widget in list_request_extras_providers()
