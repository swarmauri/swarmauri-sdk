from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql, sqlite

from tigrbl.types import SqliteUUID
from tigrbl.deps.sqlalchemy import String, _PgUUID


def test_sqlite_uuid_python_type_flags() -> None:
    assert SqliteUUID(as_uuid=True).python_type is UUID
    assert SqliteUUID(as_uuid=False).python_type is str


def test_sqlite_uuid_sqlite_bind_param_coerces_uuid_str() -> None:
    dialect = sqlite.dialect()
    type_ = SqliteUUID(as_uuid=True)
    uid = uuid4()

    assert type_.process_bind_param(uid, dialect) == str(uid)
    assert type_.process_bind_param(uid.hex, dialect) == str(uid)

    type_as_str = SqliteUUID(as_uuid=False)
    assert type_as_str.process_bind_param(uid, dialect) == str(uid)
    assert type_as_str.process_bind_param(uid.hex, dialect) == uid.hex


def test_sqlite_uuid_postgres_bind_param_returns_uuid() -> None:
    dialect = postgresql.dialect()
    type_ = SqliteUUID(as_uuid=True)
    uid = uuid4()

    assert type_.process_bind_param(uid, dialect) is uid
    assert type_.process_bind_param(str(uid), dialect) == uid

    type_as_str = SqliteUUID(as_uuid=False)
    assert type_as_str.process_bind_param(uid, dialect) == str(uid)


def test_sqlite_uuid_result_processing() -> None:
    uid = uuid4()
    sqlite_dialect = sqlite.dialect()
    pg_dialect = postgresql.dialect()

    type_ = SqliteUUID(as_uuid=True)
    assert type_.process_result_value(str(uid), sqlite_dialect) == uid
    assert type_.process_result_value(uid, pg_dialect) is uid

    type_as_str = SqliteUUID(as_uuid=False)
    assert type_as_str.process_result_value(uid, sqlite_dialect) == str(uid)
    assert type_as_str.process_result_value(str(uid), pg_dialect) == str(uid)


def test_sqlite_uuid_dialect_impls() -> None:
    sqlite_dialect = sqlite.dialect()
    pg_dialect = postgresql.dialect()

    type_as_uuid = SqliteUUID(as_uuid=True)
    sqlite_impl = type_as_uuid.load_dialect_impl(sqlite_dialect)
    pg_impl = type_as_uuid.load_dialect_impl(pg_dialect)

    assert isinstance(sqlite_impl, String)
    assert isinstance(pg_impl, _PgUUID)
    assert pg_impl.as_uuid is True

    type_as_str = SqliteUUID(as_uuid=False)
    pg_impl_str = type_as_str.load_dialect_impl(pg_dialect)
    assert isinstance(pg_impl_str, _PgUUID)
    assert pg_impl_str.as_uuid is False
