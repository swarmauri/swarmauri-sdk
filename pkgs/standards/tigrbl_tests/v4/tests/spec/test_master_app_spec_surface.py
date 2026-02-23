from __future__ import annotations

import datetime as dt

import pytest
from sqlalchemy import DateTime, Integer, String

from tigrbl.app.app_spec import AppSpec
from tigrbl.router.router_spec import RouterSpec
from tigrbl.column.column_spec import ColumnSpec
from tigrbl.column.field_spec import FieldSpec as F
from tigrbl.column.io_spec import IOSpec as IO
from tigrbl.column.storage_spec import ForeignKeySpec, StorageSpec as S
from tigrbl.op.types import OpSpec
from tigrbl.responses.types import ResponseSpec
from tigrbl.table.table_spec import TableSpec


@pytest.fixture
def v4_library_spec_parts() -> dict[str, object]:
    """Provide V4-style model refs and table specs used by the master app spec."""

    author_ref = "mypkg.models:Author"
    book_ref = "mypkg.models:Book"

    author_table = TableSpec(
        model_ref=author_ref,
        response=ResponseSpec(kind="json"),
        ops=(
            OpSpec(
                alias="create",
                target="create",
                expose_routes=True,
                expose_rpc=True,
                response=ResponseSpec(kind="json", status_code=201),
                tags=("Author",),
            ),
            OpSpec(
                alias="read",
                target="read",
                expose_routes=True,
                expose_rpc=True,
                response=ResponseSpec(kind="json", status_code=200),
                tags=("Author",),
            ),
        ),
        columns={
            "id": ColumnSpec(
                storage=S(type_=Integer, primary_key=True, nullable=False, unique=True),
                field=F(py_type=int, description="Author id"),
                io=IO(out_verbs=("read",), sortable=True, filter_ops=("eq", "in")),
            ),
            "name": ColumnSpec(
                storage=S(type_=String(200), nullable=False, index=True),
                field=F(
                    py_type=str,
                    description="Author name",
                    constraints={"min_length": 1, "max_length": 200},
                    required_in=("create",),
                ),
                io=IO(
                    in_verbs=("create", "update"),
                    out_verbs=("read", "list", "create", "update"),
                    mutable_verbs=("update",),
                    filter_ops=("eq", "ilike"),
                    sortable=True,
                ),
            ),
            "created_ts": ColumnSpec(
                storage=S(type_=DateTime(timezone=True), nullable=False),
                field=F(py_type=dt.datetime, description="Created timestamp"),
                io=IO(out_verbs=("read", "list")),
            ),
        },
        schemas=(),
        hooks=(),
        security_deps=(),
        deps=(),
    )

    book_table = TableSpec(
        model_ref=book_ref,
        response=ResponseSpec(kind="json"),
        ops=(
            OpSpec(
                alias="create",
                target="create",
                expose_routes=True,
                expose_rpc=True,
                response=ResponseSpec(kind="json", status_code=201),
                tags=("Book",),
            ),
            OpSpec(
                alias="read",
                target="read",
                expose_routes=True,
                expose_rpc=True,
                response=ResponseSpec(kind="json", status_code=200),
                tags=("Book",),
            ),
        ),
        columns={
            "id": ColumnSpec(
                storage=S(type_=Integer, primary_key=True, nullable=False, unique=True),
                field=F(py_type=int, description="Book id"),
                io=IO(
                    out_verbs=("read", "list"), sortable=True, filter_ops=("eq", "in")
                ),
            ),
            "title": ColumnSpec(
                storage=S(type_=String(256), nullable=False, index=True),
                field=F(
                    py_type=str,
                    description="Book title",
                    constraints={"min_length": 1, "max_length": 256},
                    required_in=("create",),
                ),
                io=IO(
                    in_verbs=("create", "update"),
                    out_verbs=("read", "list", "create", "update"),
                    mutable_verbs=("update",),
                    alias_in="title",
                    alias_out="title",
                    filter_ops=("eq", "ilike"),
                    sortable=True,
                ),
            ),
            "author_id": ColumnSpec(
                storage=S(
                    type_=Integer,
                    nullable=False,
                    index=True,
                    fk=ForeignKeySpec(
                        target="author.id",
                        on_delete="RESTRICT",
                        on_update="CASCADE",
                        deferrable=False,
                        initially_deferred=False,
                        match="SIMPLE",
                    ),
                ),
                field=F(py_type=int, description="Author FK", required_in=("create",)),
                io=IO(
                    in_verbs=("create", "update"),
                    out_verbs=("read", "list"),
                    mutable_verbs=("update",),
                    alias_in="authorId",
                    alias_out="authorId",
                    filter_ops=("eq", "in"),
                ),
            ),
        },
        schemas=(),
        hooks=(),
        security_deps=(),
        deps=(),
    )

    return {
        "author_table": author_table,
        "book_table": book_table,
    }


def test_master_app_spec_v4_surface_accepts_model_refs_and_router_owned_tables(
    v4_library_spec_parts: dict[str, object],
) -> None:
    rest_router = RouterSpec(
        name="library",
        prefix="/v1",
        tags=("Library",),
        response=ResponseSpec(kind="json"),
        hooks=(),
        security_deps=(),
        deps=(),
        schemas=(),
        ops=(),
        tables=(
            v4_library_spec_parts["author_table"],
            v4_library_spec_parts["book_table"],
        ),
    )

    app_spec = AppSpec(
        title="Library Service",
        version="0.1.0",
        engine={"kind": "sqlite", "async": True, "path": "./library.db"},
        response=ResponseSpec(kind="json"),
        jsonrpc_prefix="/rpc",
        system_prefix="/system",
        models=(),
        ops=(),
        routers=(rest_router,),
        schemas=(),
        hooks=(),
        security_deps=(),
        deps=(),
        middlewares=(),
        lifespan=None,
    )

    assert app_spec.routers == (rest_router,)
    assert rest_router.tables == (
        v4_library_spec_parts["author_table"],
        v4_library_spec_parts["book_table"],
    )
    assert app_spec.models == ()
