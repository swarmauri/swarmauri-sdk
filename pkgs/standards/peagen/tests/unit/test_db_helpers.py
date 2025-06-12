import enum
import pytest

from peagen.gateway.db_helpers import ensure_status_enum


class DummyResult:
    def __init__(self, value=None, rows=None):
        self._value = value
        self._rows = rows or []

    def scalar(self):
        return self._value

    def __iter__(self):
        return iter(self._rows)


class DummyConn:
    def __init__(self, exists=False, labels=None):
        self.exists = exists
        self.labels = labels or []
        self.queries = []

    async def execute(self, stmt):
        stmt_str = str(stmt)
        self.queries.append(stmt_str)
        if "SELECT EXISTS" in stmt_str:
            return DummyResult(self.exists)
        if "SELECT enumlabel" in stmt_str:
            return DummyResult(rows=[(label,) for label in self.labels])
        return DummyResult()


class DummyEngine:
    def __init__(self, conn):
        self.conn = conn

    def begin(self):
        engine_conn = self.conn

        class _Ctx:
            async def __aenter__(self_inner):
                return engine_conn

            async def __aexit__(self_inner, exc_type, exc, tb):
                pass

        return _Ctx()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ensure_status_enum_creates_if_missing():
    conn = DummyConn(exists=False)
    engine = DummyEngine(conn)
    await ensure_status_enum(engine)
    assert any("CREATE TYPE status" in q for q in conn.queries)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ensure_status_enum_adds_new_values(monkeypatch):
    class _Status(str, enum.Enum):
        pending = "pending"
        extra = "extra"

    conn = DummyConn(exists=True, labels=["pending"])
    engine = DummyEngine(conn)
    monkeypatch.setattr("peagen.gateway.db_helpers.Status", _Status)
    await ensure_status_enum(engine)
    assert any(
        "ALTER TYPE status ADD VALUE IF NOT EXISTS 'extra'" in q for q in conn.queries
    )
