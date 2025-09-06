from __future__ import annotations

from autoapi.v3.column.collect import collect_columns
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.orm.tables._base import Base
from autoapi.v3.specs import S, acol
from autoapi.v3.types import Mapped, String


class NameMixin:
    name: Mapped[str] = acol(storage=S(String, nullable=False))


class Thing(Base, GUIDPk, NameMixin):
    __tablename__ = "thing_collect_mixins"


def test_collect_columns_includes_mixin_fields():
    specs = collect_columns(Thing)
    assert "id" in specs
    assert "name" in specs
