"""Service key model for the authentication service."""

from __future__ import annotations

from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID

from autoapi.v3.column.io_spec import Pair
from autoapi.v3.column.storage_spec import ForeignKeySpec
from autoapi.v3.orm.mixins import Created, GUIDPk, LastUsed, ValidityWindow
from autoapi.v3.orm.tables._base import Base
from autoapi.v3.specs import F, IO, S, acol
from autoapi.v3.types import Mapped, PgUUID, String, relationship


class ServiceKey(Base, GUIDPk, Created, LastUsed, ValidityWindow):
    __tablename__ = "service_keys"
    __table_args__ = {
        "extend_existing": True,
        "schema": "authn",
    }

    label: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(constraints={"max_length": 120}),
    )

    def _pair_api_key(ctx):
        raw = token_urlsafe(32)
        return Pair(raw=raw, stored=sha256(raw.encode()).hexdigest())

    digest: Mapped[str] = acol(
        storage=S(String, nullable=False, unique=True),
        field=F(constraints={"max_length": 64}),
        io=IO(out_verbs=("read", "list"), allow_in=False).paired(
            _pair_api_key, alias="api_key"
        ),
    )

    service_id: Mapped[UUID] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.services.id"),
            index=True,
            nullable=False,
        ),
        field=F(py_type=UUID, required_in=("create",)),
        io=IO(in_verbs=("create",), out_verbs=("read", "list"), filter_ops=("eq",)),
    )

    _service = relationship(
        "Service",
        back_populates="_service_keys",
        lazy="joined",
    )

    @staticmethod
    def digest_of(value: str) -> str:
        return sha256(value.encode()).hexdigest()

    @property
    def raw_key(self) -> str:  # pragma: no cover - write-only
        raise AttributeError("raw_key is write-only")

    @raw_key.setter
    def raw_key(self, value: str) -> None:
        self.digest = self.digest_of(value)


__all__ = ["ServiceKey"]
