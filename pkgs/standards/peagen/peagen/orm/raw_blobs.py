from __future__ import annotations

from tigrbl.v3.orm.tables import Base
from tigrbl.v3.types import Integer, String, Mapped
from tigrbl.v3.orm.mixins import GUIDPk, Timestamped, BlobRef
from tigrbl.v3.specs import S, acol


class RawBlob(Base, GUIDPk, Timestamped, BlobRef):
    __tablename__ = "raw_blobs"
    __table_args__ = ({"schema": "peagen"},)
    mime_type: Mapped[str] = acol(storage=S(String, nullable=False))
    size: Mapped[int] = acol(storage=S(Integer, nullable=False))


__all__ = ["RawBlob"]
