from __future__ import annotations

import numpy as np
import pytest

from tigrbl import TigrblApp
from tigrbl.bindings import rpc_call
from tigrbl.engine import EngineSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.table import Table
from tigrbl.types import Mapped, String

from tigrbl_engine_numpy import numpy_engine, register


class NumpyWidget(Table, GUIDPk):
    __tablename__ = "numpy_widgets"

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
def app_and_db() -> tuple[TigrblApp, object]:
    register()
    spec = EngineSpec(
        kind="numpy",
        mapping={
            "array": np.empty((0, 2), dtype=object),
            "columns": ["id", "name"],
            "table": NumpyWidget.__tablename__,
            "pk": "id",
        },
    )
    _, session_factory = numpy_engine(mapping=spec.mapping)
    db = session_factory()

    api = TigrblApp(engine=spec)
    api.include_model(NumpyWidget, mount_router=False)
    api.initialize()
    return api, db


def _snapshot_numpy(db: object) -> list[dict[str, object]]:
    rows = db.to_dataframe()  # type: ignore[attr-defined]
    if rows.empty:
        return []
    if "id" in rows.columns:
        rows = rows.sort_values("id")
    return rows.to_dict(orient="records")


@pytest.mark.asyncio
async def test_numpy_engine_builtin_rpc_crud_ops(
    app_and_db: tuple[TigrblApp, object],
) -> None:
    app, db = app_and_db

    before = _snapshot_numpy(db)
    assert before == []

    created = await rpc_call(app, NumpyWidget, "create", {"name": "a"}, db=db)
    after_create = _snapshot_numpy(db)

    fetched = await rpc_call(app, NumpyWidget, "read", {"id": created["id"]}, db=db)
    after_read = _snapshot_numpy(db)

    updated = await rpc_call(
        app, NumpyWidget, "update", {"id": created["id"], "name": "b"}, db=db
    )
    after_update = _snapshot_numpy(db)

    replaced = await rpc_call(
        app, NumpyWidget, "replace", {"id": created["id"], "name": "c"}, db=db
    )
    after_replace = _snapshot_numpy(db)

    listed = await rpc_call(app, NumpyWidget, "list", {}, db=db)
    after_list = _snapshot_numpy(db)

    cleared = await rpc_call(
        app, NumpyWidget, "clear", {"filters": {"name": "c"}}, db=db
    )
    after_clear = _snapshot_numpy(db)

    created2 = await rpc_call(app, NumpyWidget, "create", {"name": "d"}, db=db)
    after_create2 = _snapshot_numpy(db)

    deleted = await rpc_call(app, NumpyWidget, "delete", {"id": created2["id"]}, db=db)
    after_delete = _snapshot_numpy(db)

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
