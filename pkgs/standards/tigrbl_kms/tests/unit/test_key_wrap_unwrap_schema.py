"""Test wrap/unwrap endpoint schema validation."""

from tigrbl.bindings import bind
from tigrbl_kms.orm import Key


def test_key_wrap_unwrap_schemas():
    """Test that wrap and unwrap operations have correct input/output schemas."""
    bind(Key)

    # Get schema field sets
    wrap_in = set(Key.schemas.wrap.in_.model_fields.keys())
    wrap_out = set(Key.schemas.wrap.out.model_fields.keys())
    unwrap_in = set(Key.schemas.unwrap.in_.model_fields.keys())
    unwrap_out = set(Key.schemas.unwrap.out.model_fields.keys())

    # Test wrap input schema
    assert {"key_material_b64"} <= wrap_in  # Required field
    assert {"aad_b64", "alg"} <= wrap_in  # Optional fields

    # Test wrap output schema
    assert {
        "kid",
        "version",
        "alg",
        "nonce_b64",
        "wrapped_key_b64",
        "tag_b64",
    } <= wrap_out

    # Test unwrap input schema
    assert {"wrapped_key_b64", "nonce_b64"} <= unwrap_in  # Required fields
    assert {"tag_b64", "aad_b64", "alg"} <= unwrap_in  # Optional fields

    # Test unwrap output schema
    assert {"key_material_b64"} <= unwrap_out


def test_wrap_unwrap_schema_field_consistency():
    """Test that wrap output fields match unwrap input requirements."""
    bind(Key)

    wrap_out_fields = set(Key.schemas.wrap.out.model_fields.keys())
    unwrap_in_fields = set(Key.schemas.unwrap.in_.model_fields.keys())

    # Fields that wrap produces should be consumable by unwrap
    wrap_to_unwrap_fields = {"nonce_b64", "wrapped_key_b64", "tag_b64", "aad_b64"}

    # Verify wrap produces what unwrap needs
    assert wrap_to_unwrap_fields <= wrap_out_fields
    assert wrap_to_unwrap_fields <= unwrap_in_fields


def test_wrap_unwrap_aad_field_consistency():
    """Test that aad_b64 field is properly configured for wrap/unwrap."""
    bind(Key)

    wrap_in = set(Key.schemas.wrap.in_.model_fields.keys())
    wrap_out = set(Key.schemas.wrap.out.model_fields.keys())
    unwrap_in = set(Key.schemas.unwrap.in_.model_fields.keys())

    # aad_b64 should be available in all wrap/unwrap operations
    assert "aad_b64" in wrap_in  # Can be provided as input
    assert "aad_b64" in wrap_out  # Echoed in output for unwrap
    assert "aad_b64" in unwrap_in  # Can be provided for unwrap


def test_schema_field_types():
    """Test that schema fields are present (type checking is handled by Pydantic)."""
    bind(Key)

    # Check wrap input fields exist
    wrap_in_fields = Key.schemas.wrap.in_.model_fields
    assert "key_material_b64" in wrap_in_fields
    assert wrap_in_fields["key_material_b64"].is_required()

    # Check wrap output fields exist
    wrap_out_fields = Key.schemas.wrap.out.model_fields
    assert "kid" in wrap_out_fields
    assert "version" in wrap_out_fields
    assert "wrapped_key_b64" in wrap_out_fields

    # Check unwrap input fields exist
    unwrap_in_fields = Key.schemas.unwrap.in_.model_fields
    assert "wrapped_key_b64" in unwrap_in_fields
    assert "nonce_b64" in unwrap_in_fields
    assert unwrap_in_fields["wrapped_key_b64"].is_required()
    assert unwrap_in_fields["nonce_b64"].is_required()

    # Check unwrap output fields exist
    unwrap_out_fields = Key.schemas.unwrap.out.model_fields
    assert "key_material_b64" in unwrap_out_fields
