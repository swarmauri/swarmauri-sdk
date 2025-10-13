"""OpenPGP key storage model used by the HPKS API."""

from __future__ import annotations

import datetime as dt

from tigrbl.orm.mixins import Mergeable, Timestamped
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.table import Base
from tigrbl.types import (
    Boolean,
    Integer,
    JSON,
    LargeBinary,
    Mapped,
    MutableList,
    String,
    TZDateTime,
)


class OpenPGPKey(Base, Mergeable, Timestamped):
    """Persisted representation of an OpenPGP certificate."""

    __tablename__ = "openpgp_keys"
    __resource__ = "openpgp_keys"

    fingerprint: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=String(64),
                primary_key=True,
                nullable=False,
                index=True,
            ),
            field=F(
                py_type=str,
                constraints={
                    "min_length": 16,
                    "examples": ["06DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEAD"],
                },
            ),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
                filter_ops=("eq", "ilike", "startswith"),
                sortable=True,
            ),
        )
    )
    key_id: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String(16), nullable=False, index=True),
            field=F(py_type=str, constraints={"min_length": 8}),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
                filter_ops=("eq", "ilike"),
                sortable=True,
            ),
        )
    )
    fingerprint_prefix: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String(16), nullable=False, index=True),
            field=F(py_type=str, constraints={"min_length": 8}),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
                filter_ops=("eq", "startswith"),
                sortable=True,
            ),
        )
    )
    ascii_armored: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read",),
            ),
        )
    )
    binary: Mapped[bytes] = acol(
        spec=ColumnSpec(
            storage=S(type_=LargeBinary, nullable=False),
            field=F(py_type=bytes),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read",),
            ),
        )
    )
    uids: Mapped[list[str]] = acol(
        spec=ColumnSpec(
            storage=S(type_=MutableList.as_mutable(JSON), default=list, nullable=False),
            field=F(
                py_type=list,
                constraints={"examples": ["Example User <user@example.com>"]},
            ),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )
    emails: Mapped[list[str]] = acol(
        spec=ColumnSpec(
            storage=S(type_=MutableList.as_mutable(JSON), default=list, nullable=False),
            field=F(py_type=list, constraints={"examples": ["user@example.com"]}),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )
    email_hashes: Mapped[list[str]] = acol(
        spec=ColumnSpec(
            storage=S(type_=MutableList.as_mutable(JSON), default=list, nullable=False),
            field=F(py_type=list),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read",),
            ),
        )
    )
    revoked: Mapped[bool] = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, default=False, nullable=False),
            field=F(py_type=bool),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )
    revoked_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime | None),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )
    algorithm: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String(64), nullable=True),
            field=F(py_type=str | None),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )
    bits: Mapped[int | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=True),
            field=F(py_type=int | None),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )
    primary_uid: Mapped[str | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=True),
            field=F(py_type=str | None),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )
    version: Mapped[int | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=True),
            field=F(py_type=int | None),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list"),
            ),
        )
    )


__all__ = ["OpenPGPKey"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__() -> list[str]:
    return sorted(__all__)
