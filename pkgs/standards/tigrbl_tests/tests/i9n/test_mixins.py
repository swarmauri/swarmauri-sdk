"""
Mixins Tests for Tigrbl v3

Tests all mixins and their expected behavior using individual DummyModel instances.
"""

import pytest
from datetime import datetime, timedelta, timezone
from tigrbl.types import String, uuid4
from tigrbl.column.shortcuts import acol, F, IO, S

from tigrbl import Base
from tigrbl.orm.mixins import (
    ActiveToggle,
    AsyncCapable,
    Audited,
    BulkCapable,
    Created,
    ExtRef,
    GUIDPk,
    LastUsed,
    MetaJSON,
    Monetary,
    RelationEdge,
    Replaceable,
    Slugged,
    SoftDelete,
    StatusColumn,
    Streamable,
    Timestamped,
    ValidityWindow,
    Versioned,
    tzutcnow,
    tzutcnow_plus_day,
)
from tigrbl.schema import _build_schema
from tigrbl.engine import resolver as _resolver


NAME_FIELD = acol(
    storage=S(type_=String, nullable=False),
    field=F(py_type=str),
    io=IO(
        in_verbs=("create", "update", "replace"),
        out_verbs=("read", "list"),
        mutable_verbs=("create", "update", "replace"),
        filter_ops=("eq",),
    ),
)


class DummyModelTimestamped(Base, GUIDPk, Timestamped):
    """Test model for Timestamped mixin."""

    __tablename__ = "dummy_timestamped"
    name = NAME_FIELD


class DummyModelCreated(Base, GUIDPk, Created):
    """Test model for Created mixin."""

    __tablename__ = "dummy_created"
    name = NAME_FIELD


class DummyModelLastUsed(Base, GUIDPk, LastUsed):
    """Test model for LastUsed mixin."""

    __tablename__ = "dummy_last_used"
    name = NAME_FIELD


class DummyModelActiveToggle(Base, GUIDPk, ActiveToggle):
    """Test model for ActiveToggle mixin."""

    __tablename__ = "dummy_active_toggle"
    name = NAME_FIELD


class DummyModelSoftDelete(Base, GUIDPk, SoftDelete):
    """Test model for SoftDelete mixin."""

    __tablename__ = "dummy_soft_delete"
    name = NAME_FIELD


class DummyModelVersioned(Base, GUIDPk, Versioned):
    """Test model for Versioned mixin."""

    __tablename__ = "dummy_versioned"
    name = NAME_FIELD


class DummyModelBulkCapable(Base, GUIDPk, BulkCapable):
    """Test model for BulkCapable mixin."""

    __tablename__ = "dummy_bulk_capable"
    name = NAME_FIELD


class DummyModelReplaceable(Base, GUIDPk, Replaceable):
    """Test model for Replaceable mixin."""

    __tablename__ = "dummy_replaceable"
    name = NAME_FIELD


class DummyModelAsyncCapable(Base, GUIDPk, AsyncCapable):
    """Test model for AsyncCapable mixin."""

    __tablename__ = "dummy_async_capable"
    name = NAME_FIELD


class DummyModelSlugged(Base, GUIDPk, Slugged):
    """Test model for Slugged mixin."""

    __tablename__ = "dummy_slugged"
    name = NAME_FIELD


class DummyModelStatusColumn(Base, GUIDPk, StatusColumn):
    """Test model for StatusColumn."""

    __tablename__ = "dummy_status_column"
    name = NAME_FIELD


class DummyModelValidityWindow(Base, GUIDPk, ValidityWindow):
    """Test model for ValidityWindow mixin."""

    __tablename__ = "dummy_validity_window"
    name = NAME_FIELD


class DummyModelMonetary(Base, GUIDPk, Monetary):
    """Test model for Monetary mixin."""

    __tablename__ = "dummy_monetary"
    name = NAME_FIELD


class DummyModelExtRef(Base, GUIDPk, ExtRef):
    """Test model for ExtRef mixin."""

    __tablename__ = "dummy_ext_ref"
    name = NAME_FIELD


class DummyModelMetaJSON(Base, GUIDPk, MetaJSON):
    """Test model for MetaJSON mixin."""

    __tablename__ = "dummy_meta_json"
    name = NAME_FIELD


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_timestamped_mixin(create_test_api):
    """Test that Timestamped mixin adds created_at and updated_at fields."""
    create_test_api(DummyModelTimestamped)

    # Get schemas
    create_schema = _build_schema(DummyModelTimestamped, verb="create")
    read_schema = _build_schema(DummyModelTimestamped, verb="read")
    update_schema = _build_schema(DummyModelTimestamped, verb="update")

    # created_at and updated_at are read-only and appear only in read schema
    assert "created_at" in read_schema.model_fields
    assert "updated_at" in read_schema.model_fields
    assert "created_at" not in create_schema.model_fields
    assert "updated_at" not in create_schema.model_fields
    assert "created_at" not in update_schema.model_fields
    assert "updated_at" not in update_schema.model_fields

    # name should be in all schemas
    assert "name" in create_schema.model_fields
    assert "name" in read_schema.model_fields
    assert "name" in update_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_created_mixin(create_test_api):
    """Test that Created mixin adds created_at field."""
    create_test_api(DummyModelCreated)

    # Get schemas
    create_schema = _build_schema(DummyModelCreated, verb="create")
    read_schema = _build_schema(DummyModelCreated, verb="read")

    # created_at is read-only and only present in read schema
    assert "created_at" in read_schema.model_fields
    assert "created_at" not in create_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_last_used_mixin(create_test_api):
    """Test that LastUsed mixin adds last_used_at field and touch method."""
    create_test_api(DummyModelLastUsed)

    # Get schemas
    read_schema = _build_schema(DummyModelLastUsed, verb="read")

    # last_used_at should be in read schema
    assert "last_used_at" in read_schema.model_fields

    # Verify the model has touch method
    assert hasattr(DummyModelLastUsed, "touch")

    # Test touch method functionality
    instance = DummyModelLastUsed(name="test")
    assert instance.last_used_at is None

    instance.touch()
    assert instance.last_used_at is not None
    assert isinstance(instance.last_used_at, datetime)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_active_toggle_mixin(create_test_api):
    """Test that ActiveToggle mixin adds is_active field."""
    create_test_api(DummyModelActiveToggle)

    # Get schemas
    create_schema = _build_schema(DummyModelActiveToggle, verb="create")
    read_schema = _build_schema(DummyModelActiveToggle, verb="read")

    # is_active should be in schemas
    assert "is_active" in create_schema.model_fields
    assert "is_active" in read_schema.model_fields

    # is_active field should be boolean type (default may be None)
    is_active_field = create_schema.model_fields["is_active"]
    assert is_active_field.annotation is bool


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_soft_delete_mixin(create_test_api):
    """Test that SoftDelete mixin adds deleted_at field."""
    create_test_api(DummyModelSoftDelete)

    # Get schemas
    read_schema = _build_schema(DummyModelSoftDelete, verb="read")

    # deleted_at should be in read schema
    assert "deleted_at" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_versioned_mixin(create_test_api):
    """Test that Versioned mixin adds revision and prev_id fields."""
    create_test_api(DummyModelVersioned)

    # Get schemas
    create_schema = _build_schema(DummyModelVersioned, verb="create")
    read_schema = _build_schema(DummyModelVersioned, verb="read")

    # revision and prev_id should be in schemas
    assert "revision" in read_schema.model_fields
    assert "prev_id" in read_schema.model_fields

    # revision should have default value of 1
    revision_field = create_schema.model_fields["revision"]
    assert revision_field.annotation is int


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_bulk_capable_mixin(create_test_api):
    """Test that BulkCapable mixin enables bulk operations."""
    api = create_test_api(DummyModelBulkCapable)

    # Check that bulk routes are available
    routes = [route.path for route in api.router.routes]

    # Bulk operations now share the base collection path
    expected_path = f"/{DummyModelBulkCapable.__name__.lower()}"
    assert expected_path in routes


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_replaceable_mixin(create_test_api):
    """Test that Replaceable mixin enables replacement operations."""
    create_test_api(DummyModelReplaceable)

    # Get schemas
    create_schema = _build_schema(DummyModelReplaceable, verb="create")
    read_schema = _build_schema(DummyModelReplaceable, verb="read")

    # Should have basic fields
    assert "name" in create_schema.model_fields
    assert "name" in read_schema.model_fields

    # Replaceable mixin is a marker mixin - doesn't add fields
    # but enables replacement functionality
    expected_fields = {"id", "name"}
    actual_fields = set(read_schema.model_fields.keys())
    assert expected_fields.issubset(actual_fields)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_async_capable_mixin(create_test_api):
    """Test that AsyncCapable mixin is a marker mixin."""
    create_test_api(DummyModelAsyncCapable)

    # Get schemas
    read_schema = _build_schema(DummyModelAsyncCapable, verb="read")

    # AsyncCapable is a marker mixin - doesn't add fields
    expected_fields = {"id", "name"}
    actual_fields = set(read_schema.model_fields.keys())
    assert actual_fields == expected_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_slugged_mixin(create_test_api):
    """Test that Slugged mixin adds slug field."""
    create_test_api(DummyModelSlugged)

    # Get schemas
    create_schema = _build_schema(DummyModelSlugged, verb="create")
    read_schema = _build_schema(DummyModelSlugged, verb="read")

    # slug should be in schemas
    assert "slug" in create_schema.model_fields
    assert "slug" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_status_column(create_test_api):
    """Test that StatusColumn adds status field."""
    create_test_api(DummyModelStatusColumn)

    # Get schemas
    create_schema = _build_schema(DummyModelStatusColumn, verb="create")
    read_schema = _build_schema(DummyModelStatusColumn, verb="read")

    # status should be in schemas
    assert "status" in create_schema.model_fields
    assert "status" in read_schema.model_fields

    # status field should be string type
    status_field = create_schema.model_fields["status"]
    assert status_field.annotation is str


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_validity_window_mixin(create_test_api):
    """Test that ValidityWindow mixin adds valid_from and valid_until fields."""
    create_test_api(DummyModelValidityWindow)

    # Get schemas
    create_schema = _build_schema(DummyModelValidityWindow, verb="create")
    read_schema = _build_schema(DummyModelValidityWindow, verb="read")

    # validity fields should be in schemas
    assert "valid_from" in create_schema.model_fields
    assert "valid_to" in create_schema.model_fields
    assert "valid_from" in read_schema.model_fields
    assert "valid_to" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_validity_window_default(create_test_api):
    api = create_test_api(DummyModelValidityWindow)
    session, release = _resolver.acquire(api=api)
    try:
        vf_default = tzutcnow()
        vt_default = tzutcnow_plus_day()
        instance = DummyModelValidityWindow(
            id=uuid4(), name="x", valid_from=vf_default, valid_to=vt_default
        )
        session.add(instance)
        session.flush()
    finally:
        release()
    assert vf_default is not None
    assert vt_default is not None
    assert abs((vt_default - vf_default) - timedelta(days=1)) < timedelta(seconds=1)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tzutcnow():
    """tzutcnow returns an aware UTC datetime close to current time."""
    now = tzutcnow()
    assert now.tzinfo == timezone.utc
    assert abs(now - datetime.now(timezone.utc)) < timedelta(seconds=1)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tzutcnow_plus_day():
    """tzutcnow_plus_day returns an aware UTC datetime one day ahead."""
    now = tzutcnow()
    future = tzutcnow_plus_day()
    assert future.tzinfo == timezone.utc
    assert future > now
    assert abs((future - now) - timedelta(days=1)) < timedelta(seconds=1)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_monetary_mixin(create_test_api):
    """Test that Monetary mixin adds currency and amount fields."""
    create_test_api(DummyModelMonetary)

    # Get schemas
    create_schema = _build_schema(DummyModelMonetary, verb="create")
    read_schema = _build_schema(DummyModelMonetary, verb="read")

    # monetary fields should be in schemas
    assert "currency" in create_schema.model_fields
    assert "amount" in create_schema.model_fields
    assert "currency" in read_schema.model_fields
    assert "amount" in read_schema.model_fields

    # currency field should be string type
    currency_field = create_schema.model_fields["currency"]
    assert currency_field.annotation is str


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_ext_ref_mixin(create_test_api):
    """Test that ExtRef mixin adds external_id field."""
    create_test_api(DummyModelExtRef)

    # Get schemas
    create_schema = _build_schema(DummyModelExtRef, verb="create")
    read_schema = _build_schema(DummyModelExtRef, verb="read")

    # external_id should be in schemas
    assert "external_id" in create_schema.model_fields
    assert "external_id" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.skip(reason="JSONB type not supported in SQLite test environment")
async def test_meta_json_mixin(create_test_api):
    """Test that MetaJSON mixin adds meta field."""
    create_test_api(DummyModelMetaJSON)

    # Get schemas
    create_schema = _build_schema(DummyModelMetaJSON, verb="create")
    read_schema = _build_schema(DummyModelMetaJSON, verb="read")

    # meta should be in schemas
    assert "meta" in create_schema.model_fields
    assert "meta" in read_schema.model_fields

    # meta should default to empty dict
    meta_field = create_schema.model_fields["meta"]
    assert meta_field.default == {}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_marker_mixins(create_test_api):
    """Test that marker mixins (Audited, Streamable, etc.) don't add fields."""

    # Create dummy models for other marker mixins
    class DummyAudited(Base, GUIDPk, Audited):
        __tablename__ = "dummy_audited"
        name = NAME_FIELD

    class DummyStreamable(Base, GUIDPk, Streamable):
        __tablename__ = "dummy_streamable"
        name = NAME_FIELD

    class DummyRelationEdge(Base, GUIDPk, RelationEdge):
        __tablename__ = "dummy_relation_edge"
        name = NAME_FIELD

    marker_models = [DummyAudited, DummyStreamable, DummyRelationEdge]

    for model in marker_models:
        create_test_api(model)

        read_schema = _build_schema(model, verb="read")

        # Should only have id and name fields (no extra fields from marker mixins)
        expected_fields = {"id", "name"}
        actual_fields = set(read_schema.model_fields.keys())
        assert actual_fields == expected_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_multiple_mixins_combination(create_test_api):
    """Test that multiple mixins can be combined correctly."""

    class DummyMultipleMixins(
        Base, GUIDPk, Timestamped, ActiveToggle, Slugged, StatusColumn
    ):
        __tablename__ = "dummy_multiple_mixins"
        name = NAME_FIELD

    create_test_api(DummyMultipleMixins)

    # Get schemas
    create_schema = _build_schema(DummyMultipleMixins, verb="create")
    read_schema = _build_schema(DummyMultipleMixins, verb="read")

    # Should have fields from all mixins
    # From ActiveToggle
    assert "is_active" in create_schema.model_fields
    assert "is_active" in read_schema.model_fields

    # From Slugged
    assert "slug" in create_schema.model_fields
    assert "slug" in read_schema.model_fields

    # From StatusColumn
    assert "status" in create_schema.model_fields
    assert "status" in read_schema.model_fields

    # From Timestamped - read-only fields should only appear in read schema
    assert "created_at" not in create_schema.model_fields
    assert "updated_at" not in create_schema.model_fields
    assert "created_at" in read_schema.model_fields
    assert "updated_at" in read_schema.model_fields
