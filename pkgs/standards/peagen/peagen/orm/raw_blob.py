from __future__ import annotations

from autoapi.v2.mixins import BlobRef, GUIDPk, Timestamped
from autoapi.v2.tables import Base
from autoapi.v2.types import Column, Integer, String


class RawBlob(Base, GUIDPk, Timestamped, BlobRef):
    __tablename__ = "raw_blobs"
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)


__all__ = ["RawBlob"]
