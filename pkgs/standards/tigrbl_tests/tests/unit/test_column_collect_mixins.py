from __future__ import annotations

from tigrbl import TableBase

from tigrbl.mapping.column_mro_collect import mro_collect_columns
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import S, acol
from tigrbl.types import Mapped, String


class NameMixin:
    name: Mapped[str] = acol(storage=S(String, nullable=False))


class Thing(TableBase, GUIDPk, NameMixin):
    __tablename__ = "thing_collect_mixins"


def test_collect_columns_includes_mixin_fields():
    specs = mro_collect_columns(Thing)
    assert "id" in specs
    assert "name" in specs
