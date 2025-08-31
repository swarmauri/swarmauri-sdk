# mixins_generic.py ───── all mix-ins live here
import datetime as dt
from decimal import Decimal

from .bootstrappable import Bootstrappable as Bootstrappable
from .upsertable import Upsertable as Upsertable
from .ownable import Ownable as Ownable, OwnerPolicy as OwnerPolicy
from .tenant_bound import TenantBound as TenantBound, TenantPolicy as TenantPolicy
from ...specs import ColumnSpec, F, IO, S, acol
from ...specs.storage_spec import ForeignKeySpec
from ...types import (
    TZDateTime,
    Integer,
    String,
    declarative_mixin,
    declared_attr,
    PgUUID,
    SAEnum,
    Numeric,
    Index,
    JSONB,
    TSVECTOR,
    Boolean,
    UUID,
    uuid4,
    Mapped,
)
from ...config.constants import CTX_AUTH_KEY, CTX_USER_ID_KEY, BULK_VERBS


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

CRUD_IN = ("create", "update", "replace")
CRUD_OUT = ("read", "list")
CRUD_IO = IO(in_verbs=CRUD_IN, out_verbs=CRUD_OUT, mutable_verbs=CRUD_IN)
RO_IO = IO(out_verbs=CRUD_OUT)


@declarative_mixin
class GUIDPk:
    """Universal surrogate primary key."""

    id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                primary_key=True,
                default=uuid4,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=RO_IO,
            default_factory=lambda _ctx: uuid4(),
        )
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
    def tenant_id(cls) -> Mapped[UUID]:
        schema = getattr(cls, "__tenant_table_schema__", None) or _infer_schema(cls)
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.tenants.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
        return acol(spec=spec)


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
    def user_id(cls) -> Mapped[UUID]:
        schema = getattr(cls, "__user_table_schema__", None) or _infer_schema(cls)
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.users.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class OrgMixin:
    """
    Adds user_id with a schema-qualified FK to <schema>.users.id.
    Schema is inferred from the mapped subclass's __table_args__ unless
    overridden by __user_table_schema__ on the subclass.
    """

    @declared_attr
    def org_id(cls) -> Mapped[UUID]:
        schema = getattr(cls, "__org_table_schema__", None) or _infer_schema(cls)
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.orgs.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class Principal:  # concrete table marker
    __abstract__ = True


# ────────── bounded scopes  ----------------------------------
class OwnerBound:
    owner_id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="users.id"),
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
    )

    @classmethod
    def filter_for_ctx(cls, q, ctx):
        auto_fields = ctx.get(CTX_AUTH_KEY, {})
        return q.filter(cls.owner_id == auto_fields.get(CTX_USER_ID_KEY))


class UserBound:  # membership rows
    user_id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="users.id"),
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
    )

    @classmethod
    def filter_for_ctx(cls, q, ctx):
        auto_fields = ctx.get(CTX_AUTH_KEY, {})
        return q.filter(cls.user_id == auto_fields.get(CTX_USER_ID_KEY))


# ────────── lifecycle --------------------------------------------------
@declarative_mixin
class Created:
    created_at: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, default=tzutcnow, nullable=False),
            field=F(py_type=dt.datetime),
            io=RO_IO,
        )
    )


@declarative_mixin
class LastUsed:
    last_used_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True, onupdate=tzutcnow),
            field=F(py_type=dt.datetime),
            io=RO_IO,
        )
    )

    def touch(self) -> None:
        """Mark the object as used now."""
        self.last_used_at = tzutcnow()


@declarative_mixin
class Timestamped:
    created_at: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, default=tzutcnow, nullable=False),
            field=F(py_type=dt.datetime),
            io=RO_IO,
        )
    )
    updated_at: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=TZDateTime,
                default=tzutcnow,
                onupdate=tzutcnow,
                nullable=False,
            ),
            field=F(py_type=dt.datetime),
            io=RO_IO,
        )
    )


@declarative_mixin
class ActiveToggle:
    is_active: Mapped[bool] = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, default=True, nullable=False),
            field=F(py_type=bool),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class SoftDelete:
    deleted_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )  # NULL means "live"


@declarative_mixin
class Versioned:
    revision: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, default=1, nullable=False),
            field=F(py_type=int),
            io=CRUD_IO,
        )
    )
    prev_id: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True), nullable=True),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
    )  # FK self optional


# ────────── containment & hierarchy -----------------------------------
@declarative_mixin
class Contained:
    @declared_attr
    def parent_id(cls) -> Mapped[UUID]:
        if not hasattr(cls, "parent_table"):
            raise AttributeError("subclass must set parent_table")
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{cls.parent_table}.id"),
                nullable=False,
            ),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class TreeNode:
    """
    Self-nesting hierarchy.  Works for *any* subclass because the FK
    string is built from cls.__tablename__ **after** the subclass sets it.
    """

    @declared_attr
    def parent_id(cls) -> Mapped[UUID | None]:
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{cls.__tablename__}.id"),
                nullable=True,
            ),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
        return acol(spec=spec)

    path: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )  # materialised path / ltree / etc.


# ────────── edge / link patterns --------------------------------------
@declarative_mixin
class RelationEdge:
    """Marker: row itself is an association—no extra columns required."""

    pass


@declarative_mixin
class MaskableEdge:
    """Edge row with bitmap of verbs/roles."""

    mask: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=False),
            field=F(py_type=int),
            io=CRUD_IO,
        )
    )


# ────────── execution / storage hints ---------------------------------
@declarative_mixin
class AsyncCapable:  # marker only
    # ❓ Is this required anymore or do we natively support this behavior?
    pass


@declarative_mixin
class Audited:  # marker only
    pass


@declarative_mixin
class BlobRef:
    blob_id: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True)),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
    )  # points to S3 / GCS


@declarative_mixin
class RowLock:
    lock_token: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True), nullable=True),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
    )
    locked_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )


# ────────── Bulk Operations ---------------------------------------------
@declarative_mixin
class BulkCapable:
    __autoapi_defaults_mode__: str = "all"
    __autoapi_defaults_include__: set[str] = set(
        v for v in BULK_VERBS if v not in {"bulk_replace", "bulk_merge"}
    )
    __autoapi_defaults_exclude__: set[str] = set()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        inc = set(getattr(cls, "__autoapi_defaults_include__", set()))
        inc.update(BulkCapable.__autoapi_defaults_include__)
        cls.__autoapi_defaults_include__ = inc

        exc = set(getattr(cls, "__autoapi_defaults_exclude__", set()))
        exc.update(BulkCapable.__autoapi_defaults_exclude__)
        cls.__autoapi_defaults_exclude__ = exc


# ────────── Enable PUT METHOD ------------------------------------------
@declarative_mixin
class Replaceable:
    __autoapi_defaults_mode__: str = "all"
    __autoapi_defaults_include__: set[str] = {"replace", "bulk_replace"}
    __autoapi_defaults_exclude__: set[str] = set()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        inc = set(getattr(cls, "__autoapi_defaults_include__", set()))
        inc.update(Replaceable.__autoapi_defaults_include__)
        cls.__autoapi_defaults_include__ = inc


# ────────── Enable PATCH MERGE ---------------------------------------
@declarative_mixin
class Mergeable:
    __autoapi_defaults_mode__: str = "all"
    __autoapi_defaults_include__: set[str] = {"merge", "bulk_merge"}
    __autoapi_defaults_exclude__: set[str] = set()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        inc = set(getattr(cls, "__autoapi_defaults_include__", set()))
        inc.update(Mergeable.__autoapi_defaults_include__)
        cls.__autoapi_defaults_include__ = inc


# ────────── WSS --------------------------------------------------------
@declarative_mixin
class Streamable:
    pass


# ----------------------------------------------------------------------
# Slugged ── human-readable identifier
@declarative_mixin
class Slugged:
    slug: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, unique=True, nullable=False),
            field=F(py_type=str, constraints={"max_length": 120}),
            io=CRUD_IO,
        )
    )


# ----------------------------------------------------------------------
# StatusMixin ── finite workflow states
@declarative_mixin
class StatusMixin:
    status: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=SAEnum(
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
            ),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )


# ----------------------------------------------------------------------
# ValidityWindow ── temporal availability
@declarative_mixin
class ValidityWindow:
    valid_from: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, default=tzutcnow, nullable=False),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )
    valid_to: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, default=tzutcnow_plus_day),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )


# ----------------------------------------------------------------------
# Monetary ── precise currency values (≥ 10^16, 2 decimals)
@declarative_mixin
class Monetary:
    amount: Mapped[Decimal] = acol(
        spec=ColumnSpec(
            storage=S(type_=Numeric(18, 2), nullable=False),
            field=F(py_type=Decimal),
            io=CRUD_IO,
        )
    )
    currency: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, default="USD", nullable=False),
            field=F(py_type=str, constraints={"max_length": 3}),
            io=CRUD_IO,
        )
    )


# ----------------------------------------------------------------------
# ExtRef ── link to an external provider object
@declarative_mixin
class ExtRef:
    external_id: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )  # e.g. Stripe customer ID
    provider: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )  # 'stripe', 'hubspot', …


# ----------------------------------------------------------------------
# MetaJSON ── schemaless per-row extras
@declarative_mixin
class MetaJSON:
    meta: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, default=dict),
            field=F(py_type=dict),
            io=CRUD_IO,
        )
    )


# ----------------------------------------------------------------------
# SoftLock ── pessimistic edit lock
@declarative_mixin
class SoftLock:
    locked_by: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True), fk=ForeignKeySpec(target="users.id")),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
    )
    locked_at: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )


# ----------------------------------------------------------------------
# TaggableEdge ── free-form tag on an edge row (inherits RelationEdge)
@declarative_mixin
class TaggableEdge:
    tag: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )


# ----------------------------------------------------------------------
# SearchVector ── PostgreSQL full-text search
@declarative_mixin
class SearchVector:
    tsv: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=TSVECTOR),
            field=F(py_type=str),
            io=IO(),
        )
    )

    @declared_attr
    def __table_args__(cls):
        return (Index(f"ix_{cls.__tablename__}_tsv", "tsv"),)
