# mixins_generic.py ───── all mix-ins live here
import uuid
import datetime as dt
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_mixin
from sqlalchemy import (
    Enum as SAEnum,
    Numeric,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.ext.declarative import declarative_mixin


# ----------------------------------------------------------------------


@declarative_mixin  # 1  ────────── identity
class GUIDPk:
    """Universal surrogate primary key."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


# ────────── lifecycle --------------------------------------------------
@declarative_mixin  # 2
class Timestamped:
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        nullable=False,
    )


@declarative_mixin  # 3
class SoftDelete:
    deleted_at = Column(DateTime, nullable=True)  # NULL means “live”


@declarative_mixin  # 4
class Versioned:
    revision = Column(Integer, default=1, nullable=False)
    prev_id = Column(UUID(as_uuid=True), nullable=True)  # FK self optional


# ────────── principals -----------------------------------------
@declarative_mixin
class Ownable:
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False
    )


@declarative_mixin
class Principal:  # concrete table marker
    __abstract__ = True


# ────────── bounded scopes  ----------------------------------
@declarative_mixin
class TenantBound:
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=False
    )


@declarative_mixin
class PrincipalBound:
    """
    Allows a row to belong to ANY principal type.
    principal_type: 'user' | 'group' | 'service' | 'org' | 'tenant'
    principal_id  : UUID FK into the corresponding table
    """

    principal_type = Column(String, nullable=False)
    principal_id = Column(UUID(as_uuid=True), nullable=False)


# ────────── containment & hierarchy -----------------------------------
@declarative_mixin  # 7
class Contained:
    """Generic 1→N parent relationship; parent_table string set on subclass."""

    parent_id = Column(UUID(as_uuid=True), nullable=False)

    @declared_attr
    def _parent_fk(cls):  # bound at class compile
        return ForeignKey(f"{cls.parent_table}.id")


@declarative_mixin  # 8
class TreeNode:
    """Self-nesting folder / org trees."""

    parent_id = Column(UUID(as_uuid=True), ForeignKey(lambda: f"{__name__}.id"))
    path = Column(String)  # materialised-path / ltree


# ────────── edge / link patterns --------------------------------------
@declarative_mixin  # 9
class RelationEdge:
    """Marker: row itself is an association—no extra columns required."""

    pass


@declarative_mixin  # 10
class MaskableEdge:
    """Edge row with bitmap of verbs/roles."""

    mask = Column(Integer, nullable=False)


# ────────── execution / storage hints ---------------------------------
@declarative_mixin  # 11
class AsyncCapable:  # marker only
    pass


@declarative_mixin  # 12
class Audited:  # marker only
    pass


@declarative_mixin  # 13
class BlobRef:
    blob_id = Column(UUID(as_uuid=True))  # points to S3 / GCS


@declarative_mixin  # 14
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
# 1. Slugged ── human-readable identifier
@declarative_mixin
class Slugged:
    slug = Column(String, unique=True, index=True, nullable=False)


# ----------------------------------------------------------------------
# 2. StatusEnum ── finite workflow states
@declarative_mixin
class StatusEnum:
    status = Column(
        SAEnum("draft", "active", "archived", name="status_enum"),
        default="draft",
        nullable=False,
    )


# ----------------------------------------------------------------------
# 3. ValidityWindow ── temporal availability
@declarative_mixin
class ValidityWindow:
    valid_from = Column(DateTime, default=dt.datetime.utcnow, nullable=False)
    valid_to = Column(DateTime)  # NULL → open-ended


# ----------------------------------------------------------------------
# 4. Monetary ── precise currency values (≥ 10^16, 2 decimals)
@declarative_mixin
class Monetary:
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)


# ----------------------------------------------------------------------
# 5. ExtRef ── link to an external provider object
@declarative_mixin
class ExtRef:
    external_id = Column(String, index=True)  # e.g. Stripe customer ID
    provider = Column(String)  # 'stripe', 'hubspot', …


# ----------------------------------------------------------------------
# 6. MetaJSON ── schemaless per-row extras
@declarative_mixin
class MetaJSON:
    meta = Column(JSONB, default=dict)


# ----------------------------------------------------------------------
# 7. SoftLock ── pessimistic edit lock
@declarative_mixin
class SoftLock:
    locked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    locked_at = Column(DateTime)


# ----------------------------------------------------------------------
# 8. TaggableEdge ── free-form tag on an edge row (inherits RelationEdge)
@declarative_mixin
class TaggableEdge:
    tag = Column(String, index=True, nullable=False)


# ----------------------------------------------------------------------
# 9. SearchVector ── PostgreSQL full-text search
@declarative_mixin
class SearchVector:
    tsv = Column(TSVECTOR)

    @declared_attr
    def __table_args__(cls):
        return (Index(f"ix_{cls.__tablename__}_tsv", "tsv", postgresql_using="gin"),)
