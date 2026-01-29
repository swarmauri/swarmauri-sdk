from __future__ import annotations

from enum import Enum

from tigrbl.specs import S
from tigrbl.types import PgEnum, PgUUID, SAEnum, SqliteUUID, TSVECTOR


class Status(Enum):
    ACTIVE = "active"
    PAUSED = "paused"


def test_database_specific_types() -> None:
    assert S(type_=PgUUID).type_ is PgUUID
    assert S(type_=PgEnum).type_ is PgEnum
    assert S(type_=TSVECTOR).type_ is TSVECTOR
    assert S(type_=SqliteUUID).type_ is SqliteUUID
    assert isinstance(S(type_=SAEnum(Status)).type_, SAEnum)
