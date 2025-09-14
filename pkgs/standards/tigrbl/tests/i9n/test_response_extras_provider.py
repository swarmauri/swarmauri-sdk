import pytest

from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.schema import _build_schema
from tigrbl.types import Column, Field, ResponseExtrasProvider, String
from tigrbl.types.response_extras_provider import list_response_extras_providers


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_response_extras_provider_in_schema():
    Base.metadata.clear()

    class Widget(Base, GUIDPk, ResponseExtrasProvider):
        __tablename__ = "widgets"
        name = Column(String, nullable=False)
        __tigrbl_response_extras__ = {"read": {"extra": (int | None, Field(None))}}

    SRead = _build_schema(Widget, verb="read")
    assert "extra" in SRead.model_fields
    assert Widget in list_response_extras_providers()
