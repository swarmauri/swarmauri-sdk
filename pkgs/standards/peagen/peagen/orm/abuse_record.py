from __future__ import annotations

from tigrbl.v3.orm.tables import Base, User
from tigrbl.v3.types import Boolean, Integer, String, Mapped, relationship
from tigrbl.v3.orm.mixins import GUIDPk, Timestamped, Ownable
from tigrbl.v3.specs import S, acol


class AbuseRecord(Base, GUIDPk, Timestamped, Ownable):
    """
    Track abuse metrics for a given IP address.
    • id          – surrogate UUID PK (from GUIDPk)
    • created_at  – first_seen (from Timestamped)
    • updated_at  – maintained automatically (from Timestamped)
    • owner_id    – who owns this record (from Ownable)
    """

    __tablename__ = "abuse_records"
    __table_args__ = ({"schema": "peagen"},)

    ip: Mapped[str] = acol(storage=S(String, nullable=False, unique=True, index=True))
    count: Mapped[int] = acol(storage=S(Integer, nullable=False, default=0))
    banned: Mapped[bool] = acol(storage=S(Boolean, nullable=False, default=False))

    owner: Mapped[User] = relationship(User, lazy="selectin")
