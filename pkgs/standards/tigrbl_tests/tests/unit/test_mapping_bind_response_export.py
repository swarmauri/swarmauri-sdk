import inspect

from tigrbl_concrete._mapping import model as _model


def test_mapping_bind_response_uses_responses_resolver() -> None:
    """Response schema resolution must live in tigrbl_concrete._mapping.model,
    not in the removed tigrbl.mapping namespace."""
    source = inspect.getsource(_model._resolve_schema_arg)
    # Must resolve by alias/kind from model.schemas
    assert "schemas" in source
    assert "alias" in source
    # Must NOT import from the removed tigrbl.mapping module
    assert "tigrbl.mapping" not in source
