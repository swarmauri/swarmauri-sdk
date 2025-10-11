from __future__ import annotations

import datetime as dt
from decimal import Decimal

from typing import Callable, ClassVar

from sqlalchemy.orm import synonym

from ...column import Column
from ...specs import ColumnSpec, F, IO, S, acol
from ...types import (
    TZDateTime,
    PgUUID,
    String,
    SAEnum,
    Numeric,
    JSONB,
    TSVECTOR,
    UUID,
    Index,
    declarative_mixin,
    declared_attr,
    Mapped,
)

from .utils import tzutcnow, tzutcnow_plus_day, CRUD_IO


@declarative_mixin
class Slugged:
    slug: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, unique=True, nullable=False),
            field=F(py_type=str, constraints={"max_length": 120}),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class StatusColumn:
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


@declarative_mixin
class ExtRef:
    """Attach an external identifier and provider metadata to a model."""

    #: Attribute name exposed on the SQLAlchemy model for the external id.
    __extref_external_id_attr__: ClassVar[str] = "external_id"
    #: Physical column name for the external id – defaults to the attribute name.
    __extref_external_id_column__: ClassVar[str | None] = None
    #: Optional :class:`ColumnSpec` override for the external id column.
    __extref_external_id_spec__: ClassVar[
        ColumnSpec | Callable[[type], ColumnSpec] | None
    ] = None

    #: Attribute name used for the provider column.
    __extref_provider_attr__: ClassVar[str] = "provider"
    #: Physical column name for the provider – defaults to the attribute name.
    __extref_provider_column__: ClassVar[str | None] = None
    #: Optional :class:`ColumnSpec` override for the provider column.
    __extref_provider_spec__: ClassVar[
        ColumnSpec | Callable[[type], ColumnSpec] | None
    ] = None

    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        # Only configure concrete subclasses; the mixin itself just holds defaults.
        if cls is ExtRef:
            return
        cls._extref_install()

    @classmethod
    def _extref_install(cls) -> None:
        """Ensure external id/provider columns exist with optional aliases."""

        def _resolve(
            *,
            spec_config: ColumnSpec | Callable[[type], ColumnSpec] | None,
            default: ColumnSpec,
        ) -> ColumnSpec:
            if callable(spec_config):
                return spec_config(cls)
            if spec_config is None:
                return default
            return ColumnSpec(
                storage=spec_config.storage,
                field=spec_config.field,
                io=spec_config.io,
                default_factory=spec_config.default_factory,
                read_producer=spec_config.read_producer,
            )

        ext_attr = getattr(cls, "__extref_external_id_attr__", "external_id")
        ext_col_name = getattr(cls, "__extref_external_id_column__", None) or ext_attr
        if not isinstance(cls.__dict__.get(ext_attr), Column):
            ext_spec = _resolve(
                spec_config=getattr(cls, "__extref_external_id_spec__", None),
                default=ColumnSpec(
                    storage=S(type_=String),
                    field=F(py_type=str),
                    io=CRUD_IO,
                ),
            )
            ext_col = acol(spec=ext_spec, name=ext_col_name)
            setattr(cls, ext_attr, ext_col)
            ext_col.__set_name__(cls, ext_attr)
        else:
            ext_col = getattr(cls, ext_attr)

        if ext_attr != "external_id":
            setattr(cls, "external_id", synonym(ext_attr))
            colspecs = getattr(cls, "__tigrbl_colspecs__", None)
            if colspecs is not None and ext_attr in colspecs:
                colspecs["external_id"] = colspecs[ext_attr]

        provider_attr = getattr(cls, "__extref_provider_attr__", "provider")
        provider_col_name = (
            getattr(cls, "__extref_provider_column__", None) or provider_attr
        )
        if not isinstance(cls.__dict__.get(provider_attr), Column):
            provider_spec = _resolve(
                spec_config=getattr(cls, "__extref_provider_spec__", None),
                default=ColumnSpec(
                    storage=S(type_=String),
                    field=F(py_type=str),
                    io=CRUD_IO,
                ),
            )
            provider_col = acol(spec=provider_spec, name=provider_col_name)
            setattr(cls, provider_attr, provider_col)
            provider_col.__set_name__(cls, provider_attr)
        else:
            provider_col = getattr(cls, provider_attr)

        if provider_attr != "provider":
            setattr(cls, "provider", synonym(provider_attr))
            colspecs = getattr(cls, "__tigrbl_colspecs__", None)
            if colspecs is not None and provider_attr in colspecs:
                colspecs["provider"] = colspecs[provider_attr]


@declarative_mixin
class MetaJSON:
    meta: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, default=dict),
            field=F(py_type=dict),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class BlobRef:
    blob_id: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True)),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
    )


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


__all__ = [
    "Slugged",
    "StatusColumn",
    "ValidityWindow",
    "Monetary",
    "ExtRef",
    "MetaJSON",
    "BlobRef",
    "SearchVector",
]
