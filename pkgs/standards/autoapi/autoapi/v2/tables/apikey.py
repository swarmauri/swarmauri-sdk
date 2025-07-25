from __future__ import annotations


from ..types import Column, String, UniqueConstraint
from ._base import Base
from ..mixins import (
    GUIDPk,
    UserMixin,
    Created,
    LastUsed,
    ValidityWindow,
)


# ------------------------------------------------------------------ model
class ApiKey(
    Base,
    GUIDPk,
    UserMixin,  # FK → user.id and back‑populates
    Created,  # created_at timestamp
    LastUsed,  # last_used_at timestamp
    ValidityWindow,  # expires_at
):
    __tablename__ = "apikeys"
    __table_args__ = (
        UniqueConstraint("digest"),
        {"extend_existing": True},
    )

    label = Column(String(120), nullable=False)

    digest = Column(
        String(64),
        nullable=False,
        unique=True,
        info={
            "autoapi": {
                # hide from Create / Update / Replace verbs
                "disable_on": ["create", "update", "replace"],
                # show in READ / LIST responses only
                "read_only": True,
            }
        },
    )
