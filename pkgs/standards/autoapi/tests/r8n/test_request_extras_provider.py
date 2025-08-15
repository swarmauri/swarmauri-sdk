import pytest

from autoapi.v3 import Base
from autoapi.v3.types import Column, String, Field, RequestExtrasProvider
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.impl.schema import _schema
from autoapi.v3.types.request_extras_provider import list_request_extras_providers


@pytest.mark.r8n
@pytest.mark.asyncio
async def test_request_extras_provider_in_schema():
    Base.metadata.clear()

    class Widget(Base, GUIDPk, RequestExtrasProvider):
        __tablename__ = "widgets"
        name = Column(String, nullable=False)
        __autoapi_request_extras__ = {
            "create": {"extra": (int | None, Field(None, exclude=True))}
        }

    SCreate = _schema(Widget, verb="create")
    SRead = _schema(Widget, verb="read")

    assert "extra" in SCreate.model_fields
    assert "extra" not in SRead.model_fields
    assert Widget in list_request_extras_providers()
