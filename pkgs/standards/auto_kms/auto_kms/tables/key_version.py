from __future__ import annotations

from autoapi.v3.types import (
    Integer,
    LargeBinary,
    SAEnum,
    UniqueConstraint,
    relationship,
    PgUUID,
)
from sqlalchemy.orm import Mapped
from uuid import UUID
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped
from autoapi.v3.specs import acol, S, IO, F
from autoapi.v3.specs.storage_spec import ForeignKeySpec
from autoapi.v3.decorators import hook_ctx

from ..utils import b64d


class KeyVersion(Base, GUIDPk, Timestamped):
    __tablename__ = "key_versions"
    __resource__ = "key_version"
    __table_args__ = (UniqueConstraint("key_id", "version"),)

    key_id: Mapped[UUID] = acol(
        storage=S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="keys.id", on_delete="CASCADE"),
            nullable=False,
            index=True,
        ),
        field=F(py_type=UUID, required_in=("create",)),
        io=IO(
            in_verbs=("create",),
            out_verbs=("read", "list"),
            filter_ops=("eq",),
        ),
    )

    version: Mapped[int] = acol(
        storage=S(type_=Integer, nullable=False),
        field=F(py_type=int, required_in=("create",)),
        io=IO(in_verbs=("create",), out_verbs=("read", "list"), sortable=True),
    )

    status: Mapped[str] = acol(
        storage=S(
            type_=SAEnum(
                "active",
                name="VersionStatus",
                native_enum=True,
                validate_strings=True,
                create_constraint=True,
            ),
            nullable=False,
        ),
        field=F(py_type=str, required_in=("create",)),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    public_material: Mapped[bytes | memoryview | None] = acol(
        storage=S(type_=LargeBinary, nullable=True),
        io=IO(alias_in="public_material_b64", in_verbs=("create", "update")),
    )

    @hook_ctx(ops=("create", "update"), phase="PRE_FLUSH")
    def _decode_material(cls, ctx):
        p = ctx.get("payload") or {}
        raw = p.get("public_material_b64")
        if raw is not None:
            ctx["object"].public_material = b64d(raw)

    key = relationship("Key", back_populates="versions", lazy="joined")
