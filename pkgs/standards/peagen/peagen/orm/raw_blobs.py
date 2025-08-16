from __future__ import annotations

from autoapi.v3.tables import Base
from autoapi.v3.types import Column, String, Integer
from autoapi.v3.mixins import GUIDPk, Timestamped, BlobRef


class RawBlob(Base, GUIDPk, Timestamped, BlobRef):
    __tablename__ = "raw_blobs"
    __table_args__ = ({"schema": "peagen"},)
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)


__all__ = ["RawBlob"]
