# mixins_generic.py ───── all mix-ins live here
import uuid
import datetime as dt
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_mixin, declared_attr
from sqlalchemy import (
    Enum as SAEnum,
    Numeric,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

# ----------------------------------------------------------------------


@declarative_mixin
class GUIDPk:
    """Universal surrogate primary key."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


# ────────── principals -----------------------------------------
@declarative_mixin
class Ownable:
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False
    )


class TenantMixin:
    tenant_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("tenants.id"))


@declarative_mixin
class UserMixin:
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False
    )


@declarative_mixin
class Principal:  # concrete table marker
    __abstract__ = True


# ────────── bounded scopes  ----------------------------------
class OwnerBound:
    owner_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id"))

    @classmethod
    def filter_for_ctx(cls, q, ctx):
        return q.filter(cls.owner_id == ctx.user_id)


class UserBound:  # membership rows
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("users.id"))

    @classmethod
    def filter_for_ctx(cls, q, ctx):
        return q.filter(cls.user_id == ctx.user_id)


class TenantBound:
    tenant_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("tenants.id"))

    @classmethod
    def filter_for_ctx(cls, q, ctx):
        return q.filter(cls.tenant_id == ctx.tenant_id)


# ────────── lifecycle --------------------------------------------------
@declarative_mixin
class Timestamped:
    created_at = Column(
        DateTime,
        default=dt.datetime.utcnow,
        nullable=False,
        info=dict(no_create=True, no_update=True),
    )
    updated_at = Column(
        DateTime,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        nullable=False,
        info=dict(no_create=True, no_update=True),
    )


@declarative_mixin
class SoftDelete:
    deleted_at = Column(DateTime, nullable=True)  # NULL means “live”


@declarative_mixin
class Versioned:
    revision = Column(Integer, default=1, nullable=False)
    prev_id = Column(UUID(as_uuid=True), nullable=True)  # FK self optional


# ────────── containment & hierarchy -----------------------------------
@declarative_mixin
class Contained:
    @declared_attr
    def parent_id(cls):
        if not hasattr(cls, "parent_table"):
            raise AttributeError("subclass must set parent_table")
        return Column(
            UUID(as_uuid=True), ForeignKey(f"{cls.parent_table}.id"), nullable=False
        )


@declarative_mixin
class TreeNode:
    """
    Self-nesting hierarchy.  Works for *any* subclass because the FK
    string is built from cls.__tablename__ **after** the subclass sets it.
    """

    @declared_attr
    def parent_id(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey(f"{cls.__tablename__}.id"),  # << string, not lambda
            nullable=True,
        )

    path = Column(String)  # materialised path / ltree / etc.


# ────────── edge / link patterns --------------------------------------
@declarative_mixin
class RelationEdge:
    """Marker: row itself is an association—no extra columns required."""

    pass


@declarative_mixin
class MaskableEdge:
    """Edge row with bitmap of verbs/roles."""

    mask = Column(Integer, nullable=False)


# ────────── execution / storage hints ---------------------------------
@declarative_mixin
class AsyncCapable:  # marker only
    pass


@declarative_mixin
class Audited:  # marker only
    pass


@declarative_mixin
class BlobRef:
    blob_id = Column(UUID(as_uuid=True))  # points to S3 / GCS


@declarative_mixin
class RowLock:
    lock_token = Column(UUID(as_uuid=True), nullable=True)
    locked_at = Column(DateTime, nullable=True)


# ────────── Bulk Operations ---------------------------------------------
@declarative_mixin
class BulkCapable:
    pass


# ────────── Enable PUT METHOD ------------------------------------------
@declarative_mixin
class Replaceable:
    pass  # described earlier


# ────────── WSS --------------------------------------------------------
@declarative_mixin
class Streamable:
    pass


# ----------------------------------------------------------------------
# Slugged ── human-readable identifier
@declarative_mixin
class Slugged:
    slug = Column(String, unique=True, nullable=False)


# ----------------------------------------------------------------------
# StatusMixin ── finite workflow states
@declarative_mixin
class StatusMixin:
    status = Column(
        SAEnum(
            "queued",
            "waiting",
            "input_required",
            "auth_required",
            "approved",
            "rejected",
            "dispatched",
            "running",
            "paused",
            "success",
            "failed",
            "cancelled",
            name="status_enum",
        ),
        default="waiting",
        nullable=False,
    )


# ----------------------------------------------------------------------
# ValidityWindow ── temporal availability
@declarative_mixin
class ValidityWindow:
    valid_from = Column(DateTime, default=dt.datetime.utcnow, nullable=False)
    valid_to = Column(DateTime)


# ----------------------------------------------------------------------
# Monetary ── precise currency values (≥ 10^16, 2 decimals)
@declarative_mixin
class Monetary:
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)


# ----------------------------------------------------------------------
# ExtRef ── link to an external provider object
@declarative_mixin
class ExtRef:
    external_id = Column(String)  # e.g. Stripe customer ID
    provider = Column(String)  # 'stripe', 'hubspot', …


# ----------------------------------------------------------------------
# MetaJSON ── schemaless per-row extras
@declarative_mixin
class MetaJSON:
    meta = Column(JSONB, default=dict)


# ----------------------------------------------------------------------
# SoftLock ── pessimistic edit lock
@declarative_mixin
class SoftLock:
    locked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    locked_at = Column(DateTime)


# ----------------------------------------------------------------------
# TaggableEdge ── free-form tag on an edge row (inherits RelationEdge)
@declarative_mixin
class TaggableEdge:
    tag = Column(String, nullable=False)


# ----------------------------------------------------------------------
# SearchVector ── PostgreSQL full-text search
@declarative_mixin
class SearchVector:
    tsv = Column(TSVECTOR)

    @declared_attr
    def __table_args__(cls):
        return (Index(f"ix_{cls.__tablename__}_tsv", "tsv"),)
