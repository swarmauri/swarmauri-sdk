# mixins_generic.py ───── all mix-ins live here
import datetime as dt
from .bootstrappable import Bootstrappable as Bootstrappable
from .upsertable import Upsertable as Upsertable
from .ownable import Ownable as Ownable, OwnerPolicy as OwnerPolicy
from .tenant_bound import TenantBound as TenantBound, TenantPolicy as TenantPolicy
from ..types import (
    Column,
    TZDateTime,
    Integer,
    String,
    ForeignKey,
    declarative_mixin,
    declared_attr,
    PgUUID,
    SAEnum,
    Numeric,
    Index,
    Mapped,
    mapped_column,
    JSONB,
    TSVECTOR,
    Boolean,
    UUID,
    uuid4,
)
from ..cfgs import AUTH_CONTEXT_KEY, USER_ID_KEY


def tzutcnow() -> dt.datetime:  # default/on‑update factory
    """Return an **aware** UTC `datetime`."""
    return dt.datetime.now(dt.timezone.utc)


def tzutcnow_plus_day() -> dt.datetime:
    """Return an aware UTC ``datetime`` one day in the future."""
    return tzutcnow() + dt.timedelta(days=1)


def _infer_schema(cls, default: str = "public") -> str:
    """Extract schema from __table_args__ in dict or tuple/list form."""
    args = getattr(cls, "__table_args__", None)
    if not args:
        return default
    if isinstance(args, dict):
        return args.get("schema", default)
    if isinstance(args, (tuple, list)):
        for elem in args:
            if isinstance(elem, dict) and "schema" in elem:
                return elem["schema"]
    return default


# ----------------------------------------------------------------------

uuid_example = UUID("00000000-dead-beef-cafe-000000000000")


@declarative_mixin
class GUIDPk:
    """Universal surrogate primary key."""

    id = Column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        info=dict(
            tigrbl={
                "default_factory": uuid4,
                "read_only": {"create": True},
                "examples": [uuid_example],
            }
        ),
    )


# ────────── principals -----------------------------------------


@declarative_mixin
class TenantMixin:
    """
    Adds tenant_id with a schema-qualified FK to <schema>.tenants.id.
    Schema is inferred from the mapped subclass's __table_args__ unless
    overridden by __tenant_table_schema__ on the subclass.
    """

    @declared_attr
    def tenant_id(cls) -> Mapped[PgUUID]:
        schema = getattr(cls, "__tenant_table_schema__", None) or _infer_schema(cls)
        return mapped_column(
            PgUUID(as_uuid=True),
            ForeignKey(f"{schema}.tenants.id"),
            nullable=False,
            index=True,
            info=dict(tigrbl={"examples": [uuid_example]}),
        )


# ──────────────────────────────────────────────────────────────────────────────
# User FK mixin
# ──────────────────────────────────────────────────────────────────────────────
@declarative_mixin
class UserMixin:
    """
    Adds user_id with a schema-qualified FK to <schema>.users.id.
    Schema is inferred from the mapped subclass's __table_args__ unless
    overridden by __user_table_schema__ on the subclass.
    """

    @declared_attr
    def user_id(cls) -> Mapped[PgUUID]:
        schema = getattr(cls, "__user_table_schema__", None) or _infer_schema(cls)
        return mapped_column(
            PgUUID(as_uuid=True),
            ForeignKey(f"{schema}.users.id"),
            nullable=False,
            index=True,
            info=dict(tigrbl={"examples": [uuid_example]}),
        )


@declarative_mixin
class OrgMixin:
    """
    Adds user_id with a schema-qualified FK to <schema>.users.id.
    Schema is inferred from the mapped subclass's __table_args__ unless
    overridden by __user_table_schema__ on the subclass.
    """

    @declared_attr
    def org_id(cls) -> Mapped[PgUUID]:
        schema = getattr(cls, "__org_table_schema__", None) or _infer_schema(cls)
        return mapped_column(
            PgUUID(as_uuid=True),
            ForeignKey(f"{schema}.orgs.id"),
            nullable=False,
            index=True,
            info=dict(tigrbl={"examples": [uuid_example]}),
        )


@declarative_mixin
class Principal:  # concrete table marker
    __abstract__ = True


# ────────── bounded scopes  ----------------------------------
class OwnerBound:
    owner_id: Mapped[PgUUID] = mapped_column(
        PgUUID,
        ForeignKey("users.id"),
        info=dict(tigrbl={"examples": [uuid_example]}),
    )

    @classmethod
    def filter_for_ctx(cls, q, ctx):
        auto_fields = ctx.get(AUTH_CONTEXT_KEY, {})
        return q.filter(cls.owner_id == auto_fields.get(USER_ID_KEY))


class UserBound:  # membership rows
    user_id: Mapped[PgUUID] = mapped_column(
        PgUUID,
        ForeignKey("users.id"),
        info=dict(tigrbl={"examples": [uuid_example]}),
    )

    @classmethod
    def filter_for_ctx(cls, q, ctx):
        auto_fields = ctx.get(AUTH_CONTEXT_KEY, {})
        return q.filter(cls.user_id == auto_fields.get(USER_ID_KEY))


# ────────── lifecycle --------------------------------------------------
@declarative_mixin
class Created:
    created_at = Column(
        TZDateTime,
        default=tzutcnow,
        nullable=False,
        info=dict(no_create=True, no_update=True),
    )


@declarative_mixin
class LastUsed:
    last_used_at = Column(
        TZDateTime,
        nullable=True,
        onupdate=tzutcnow,
        info=dict(no_create=True, no_update=True),
    )

    def touch(self) -> None:
        """Mark the object as used now."""
        self.last_used_at = tzutcnow()


@declarative_mixin
class Timestamped:
    created_at = Column(
        TZDateTime,
        default=tzutcnow,
        nullable=False,
        info=dict(no_create=True, no_update=True),
    )
    updated_at = Column(
        TZDateTime,
        default=tzutcnow,
        onupdate=tzutcnow,
        nullable=False,
        info=dict(no_create=True, no_update=True),
    )


@declarative_mixin
class ActiveToggle:
    is_active = Column(Boolean, default=True, nullable=False)


@declarative_mixin
class SoftDelete:
    deleted_at = Column(TZDateTime, nullable=True)  # NULL means “live”


@declarative_mixin
class Versioned:
    revision = Column(Integer, default=1, nullable=False)
    prev_id = Column(PgUUID(as_uuid=True), nullable=True)  # FK self optional


# ────────── containment & hierarchy -----------------------------------
@declarative_mixin
class Contained:
    @declared_attr
    def parent_id(cls):
        if not hasattr(cls, "parent_table"):
            raise AttributeError("subclass must set parent_table")
        return Column(
            PgUUID(as_uuid=True), ForeignKey(f"{cls.parent_table}.id"), nullable=False
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
            PgUUID(as_uuid=True),
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
    blob_id = Column(PgUUID(as_uuid=True))  # points to S3 / GCS


@declarative_mixin
class RowLock:
    lock_token = Column(PgUUID(as_uuid=True), nullable=True)
    locked_at = Column(TZDateTime, nullable=True)


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
    slug = Column(String(120), unique=True, nullable=False)


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
    valid_from = Column(TZDateTime, default=tzutcnow, nullable=False)
    valid_to = Column(TZDateTime, default=tzutcnow_plus_day)


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
    locked_by = Column(PgUUID(as_uuid=True), ForeignKey("users.id"))
    locked_at = Column(TZDateTime)


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
