from __future__ import annotations

from tigrbl.v3.column.mro_collect import mro_collect_columns
from tigrbl.v3.orm.mixins import GUIDPk
from tigrbl.v3.orm.tables._base import Base
from tigrbl.v3.specs import S, acol
from tigrbl.v3.types import Mapped, String


class NameMixin:
    name: Mapped[str] = acol(storage=S(String, nullable=False))


class Thing(Base, GUIDPk, NameMixin):
    __tablename__ = "thing_collect_mixins"


def test_collect_columns_includes_mixin_fields():
    specs = mro_collect_columns(Thing)
    assert "id" in specs
    assert "name" in specs
