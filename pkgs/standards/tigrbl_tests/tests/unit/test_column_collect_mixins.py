from __future__ import annotations

from tigrbl_core._spec.column_spec import mro_collect_columns
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl._spec import S
from tigrbl.shortcuts.column import acol
from tigrbl.types import Mapped, String


class NameMixin:
    name: Mapped[str] = acol(storage=S(String, nullable=False))


class Thing(TableBase, GUIDPk, NameMixin):
    __tablename__ = "thing_collect_mixins"


def test_collect_columns_includes_mixin_fields():
    specs = mro_collect_columns(Thing)
    assert "id" in specs
    assert "name" in specs
