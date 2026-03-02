import pytest
from tigrbl import TableBase
from tigrbl.orm.mixins import GUIDPk
from tigrbl.schema import _build_schema
from tigrbl.types import Column, Field, ResponseExtrasProvider, String
from tigrbl.types.response_extras_provider import list_response_extras_providers


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_response_extras_provider_in_schema():
    TableBase.metadata.clear()

    class Widget(TableBase, GUIDPk, ResponseExtrasProvider):
        __tablename__ = "widgets"
        name = Column(String, nullable=False)
        __tigrbl_response_extras__ = {"read": {"extra": (int | None, Field(None))}}

    SRead = _build_schema(Widget, verb="read")
    assert "extra" in SRead.model_fields
    assert Widget in list_response_extras_providers()


@pytest.mark.i9n
def test_response_extras_property_type_in_schema():
    TableBase.metadata.clear()

    class WidgetWithPropertyExtra(TableBase, GUIDPk, ResponseExtrasProvider):
        __tablename__ = "widgets_with_property_extra"
        name = Column(String, nullable=False)

        @property
        def hookz(self) -> list[str]:
            return ["create"]

        __tigrbl_response_extras__ = {"read": {"hookz": (hookz, Field(None))}}

    schema = _build_schema(WidgetWithPropertyExtra, verb="read")
    assert "hookz" in schema.model_fields
    assert schema.model_fields["hookz"].annotation == list[str]
