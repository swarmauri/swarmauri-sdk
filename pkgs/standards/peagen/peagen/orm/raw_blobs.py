from __future__ import annotations

from tigrbl.orm.tables import Base
from tigrbl.types import Integer, String, Mapped
from tigrbl.orm.mixins import GUIDPk, Timestamped, BlobRef
from tigrbl.specs import S, acol


class RawBlob(Base, GUIDPk, Timestamped, BlobRef):
    __tablename__ = "raw_blobs"
    __table_args__ = ({"schema": "peagen"},)
    mime_type: Mapped[str] = acol(storage=S(String, nullable=False))
    size: Mapped[int] = acol(storage=S(Integer, nullable=False))


__all__ = ["RawBlob"]
