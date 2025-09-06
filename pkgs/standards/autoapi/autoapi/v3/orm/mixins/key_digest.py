from __future__ import annotations

from hashlib import sha256
from secrets import token_urlsafe

from sqlalchemy import event

from ...column.io_spec import Pair
from ...specs import F, IO, S, acol
from ...types import Mapped, String, declarative_mixin


@declarative_mixin
class KeyDigest:
    """Provides hashed API key storage with helpers."""

    @staticmethod
    def _generate_pair() -> Pair:
        raw = token_urlsafe(32)
        return Pair(raw=raw, stored=sha256(raw.encode()).hexdigest())

    digest: Mapped[str] = acol(
        storage=S(String, nullable=False, unique=True),
        field=F(constraints={"max_length": 64}),
        io=IO(out_verbs=("read", "list", "create")).alias_readtime(
            "api_key",
            lambda obj, ctx: getattr(obj, "_api_key", None),
            verbs=("create",),
        ),
    )

    @classmethod
    def __declare_last__(cls) -> None:  # pragma: no cover - SQLAlchemy hook
        @event.listens_for(cls, "before_insert", propagate=True)
        def _set_digest(_mapper, _conn, target) -> None:
            if not getattr(target, "digest", None):
                pair = cls._generate_pair()
                target.digest = pair.stored
                setattr(target, "_api_key", pair.raw)

    @staticmethod
    def digest_of(value: str) -> str:
        return sha256(value.encode()).hexdigest()

    @property
    def raw_key(self) -> str:  # pragma: no cover - write-only
        raise AttributeError("raw_key is write-only")

    @raw_key.setter
    def raw_key(self, value: str) -> None:
        self.digest = self.digest_of(value)
