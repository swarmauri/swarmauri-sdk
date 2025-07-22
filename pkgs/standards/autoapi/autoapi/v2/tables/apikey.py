from __future__ import annotations


from ..types import (
    Column,
    String,
    relationship,
    UniqueConstraint,
    hybrid_property,
)
from ._base import Base
from ..mixins import (
    GUIDPk,
    UserMixin,
    Created,
    LastUsed,
    ValidityWindow,
    ActiveToggle,
)
from hashlib import blake2b
from secrets import token_urlsafe
from .user import User


def get_token_urlsafe_factory():
    return token_urlsafe(8)


# ------------------------------------------------------------------ model
class ApiKey(
    Base,
    GUIDPk,
    UserMixin,  # FK → user.id and back‑populates
    Created,  # created_at timestamp
    LastUsed,  # last_used_at timestamp
    ValidityWindow,  # expires_at
    ActiveToggle,  # is_active
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

    user = relationship(
        User,
        back_populates="api_keys",
        lazy="joined",  # optional: eager load to avoid N+1
    )

    @hybrid_property
    def raw_key(self) -> str:
        """Write-only virtual attribute (never returned)."""
        raise AttributeError("raw_key is write-only")

    @raw_key.setter
    def raw_key(self, value: str) -> None:
        self.digest = blake2b(value.encode(), digest_size=32).hexdigest()

    @staticmethod
    def digest_of(value: str) -> None:
        return blake2b(value.encode(), digest_size=32).hexdigest()

    # attach ColumnInfo so AutoAPI knows to expose it
    raw_key.default = get_token_urlsafe_factory
    raw_key.nullable = True
    raw_key.oncreate = get_token_urlsafe_factory
    raw_key.onupdate = get_token_urlsafe_factory
    raw_key.info = {
        "autoapi": {
            "hybrid": True,  # ← opt-in
            "write_only": True,  # hide on READ/LIST
            "py_type": str,
            "default_factory": get_token_urlsafe_factory,
            "examples": [get_token_urlsafe_factory()],  # Swagger placeholder
        }
    }
