from __future__ import annotations

from autoapi.v3.types import (
    Column,
    Integer,
    LargeBinary,
    SAEnum,
    ForeignKey,
    UniqueConstraint,
    relationship,
    PgUUID,
)
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped


class KeyVersion(Base, GUIDPk, Timestamped):
    __tablename__ = "key_versions"
    __resource__ = "key_version"
    __table_args__ = (UniqueConstraint("key_id", "version"),)

    key_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("keys.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(Integer, nullable=False)
    status = Column(SAEnum("active", name="VersionStatus"), nullable=False)
    public_material = Column(
        LargeBinary,
        nullable=True,
        info={
            "autoapi": {
                "disable_on": ["update", "replace"],
                "read_only": True,
            }
        },
    )

    key = relationship("Key", back_populates="versions", lazy="joined")
