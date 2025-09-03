from __future__ import annotations


from hashlib import sha256
from secrets import token_urlsafe

from ...specs import F, IO, S, acol
from ...types import Mapped, String
from ...column.io_spec import Pair
from ._base import Base
from ..mixins import (
    GUIDPk,
    Created,
    LastUsed,
    ValidityWindow,
)


# ------------------------------------------------------------------ model
class ApiKey(Base, GUIDPk, Created, LastUsed, ValidityWindow):
    __tablename__ = "api_keys"
    __abstract__ = True

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
        io=IO(out_verbs=("read", "list")).paired(
            _pair_api_key, alias="api_key", verbs=("create",)
        ),
    )

    # ------------------------------------------------------------------
    # Digest helpers
    # ------------------------------------------------------------------
    @staticmethod
    def digest_of(value: str) -> str:
        return sha256(value.encode()).hexdigest()

    @property
    def raw_key(self) -> str:  # pragma: no cover - write-only
        raise AttributeError("raw_key is write-only")

    @raw_key.setter
    def raw_key(self, value: str) -> None:
        self.digest = self.digest_of(value)
