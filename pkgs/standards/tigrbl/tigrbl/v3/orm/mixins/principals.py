from __future__ import annotations

from ...specs import ColumnSpec, F, S, acol
from ...specs.storage_spec import ForeignKeySpec
from ...types import PgUUID, UUID, declarative_mixin, declared_attr, uuid4, Mapped

from .utils import _infer_schema, uuid_example, CRUD_IO, RO_IO


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
        )
    )


@declarative_mixin
class TenantColumn:
    """Adds ``tenant_id`` with a schema-qualified FK to ``<schema>.tenants.id``."""

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


@declarative_mixin
class UserColumn:
    """Adds ``user_id`` with a schema-qualified FK to ``<schema>.users.id``."""

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
class OrgColumn:
    """Adds ``org_id`` with a schema-qualified FK to ``<schema>.orgs.id``."""

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
class Principal:
    __abstract__ = True


__all__ = [
    "GUIDPk",
    "TenantColumn",
    "UserColumn",
    "OrgColumn",
    "Principal",
]
