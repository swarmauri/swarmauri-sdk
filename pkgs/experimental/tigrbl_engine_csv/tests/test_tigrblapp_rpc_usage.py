from __future__ import annotations

from pathlib import Path

import pytest

from tigrbl import TigrblApp
from tigrbl.bindings import rpc_call
from tigrbl.engine import EngineSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.table import Table
from tigrbl.types import Mapped, String

from tigrbl_engine_csv import csv_engine, register


class CsvWidget(Table, GUIDPk):
    __tablename__ = "csv_widgets"

    name: Mapped[str] = acol(
        storage=S(type_=String(50), nullable=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            mutable_verbs=("create", "update", "replace"),
        ),
    )


@pytest.fixture()
def app_and_db(tmp_path: Path) -> tuple[TigrblApp, object]:
    register()
    csv_path = tmp_path / "widgets.csv"
    csv_path.write_text("id,name\n", encoding="utf-8")

    spec = EngineSpec(
        kind="csv",
        mapping={"path": str(csv_path), "table": CsvWidget.__tablename__, "pk": "id"},
    )
    _, session_factory = csv_engine(mapping=spec.mapping)
    db = session_factory()

    api = TigrblApp(engine=spec)
    api.include_model(CsvWidget, mount_router=False)
    api.initialize()
    return api, db


def _snapshot_csv(db: object) -> list[dict[str, object]]:
    rows = db.table().copy()  # type: ignore[attr-defined]
    if rows.empty:
        return []
    if "id" in rows.columns:
        rows = rows.sort_values("id")
    return rows.to_dict(orient="records")


@pytest.mark.asyncio
async def test_csv_engine_builtin_rpc_crud_ops(
    app_and_db: tuple[TigrblApp, object],
) -> None:
    app, db = app_and_db

    before = _snapshot_csv(db)
    assert before == []

    created = await rpc_call(app, CsvWidget, "create", {"name": "a"}, db=db)
    after_create = _snapshot_csv(db)

    fetched = await rpc_call(app, CsvWidget, "read", {"id": created["id"]}, db=db)
    after_read = _snapshot_csv(db)

    updated = await rpc_call(
        app, CsvWidget, "update", {"id": created["id"], "name": "b"}, db=db
    )
    after_update = _snapshot_csv(db)

    replaced = await rpc_call(
        app, CsvWidget, "replace", {"id": created["id"], "name": "c"}, db=db
    )
    after_replace = _snapshot_csv(db)

    listed = await rpc_call(app, CsvWidget, "list", {}, db=db)
    after_list = _snapshot_csv(db)

    cleared = await rpc_call(app, CsvWidget, "clear", {"filters": {"name": "c"}}, db=db)
    after_clear = _snapshot_csv(db)

    created2 = await rpc_call(app, CsvWidget, "create", {"name": "d"}, db=db)
    after_create2 = _snapshot_csv(db)

    deleted = await rpc_call(app, CsvWidget, "delete", {"id": created2["id"]}, db=db)
    after_delete = _snapshot_csv(db)

    assert fetched["id"] == created["id"]
    assert updated["name"] == "b"
    assert replaced["name"] == "c"
    assert len(listed) == 1
    assert cleared == {"deleted": 1}
    assert deleted == {"deleted": 1}

    assert after_create == [{"id": created["id"], "name": "a"}]
    assert after_read == after_create
    assert after_update == [{"id": created["id"], "name": "b"}]
    assert after_replace == [{"id": created["id"], "name": "c"}]
    assert after_list == after_replace
    assert after_clear == []
    assert after_create2 == [{"id": created2["id"], "name": "d"}]
    assert after_delete == []
