from __future__ import annotations

from tigrbl.column.mro_collect import mro_collect_columns
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables._base import Base
from tigrbl.specs import S, acol
from tigrbl.types import Mapped, String


class NameMixin:
    name: Mapped[str] = acol(storage=S(String, nullable=False))


class Thing(Base, GUIDPk, NameMixin):
    __tablename__ = "thing_collect_mixins"


def test_collect_columns_includes_mixin_fields():
    specs = mro_collect_columns(Thing)
    assert "id" in specs
    assert "name" in specs
