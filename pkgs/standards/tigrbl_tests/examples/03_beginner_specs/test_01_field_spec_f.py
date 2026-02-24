from tigrbl.specs import F


def test_field_spec_describes_python_type():
    """Show that ``F`` captures Python-level field intent.

    Purpose: introduce the field spec as the source of truth for Python types
    and descriptive metadata used by serializers and docs.

    Best practice: document field intent at the spec layer so API contracts
    stay clear even when storage types are more complex.
    """
    # Setup: create a field spec that declares Python type and description.
    field_spec = F(py_type=int, constraints={"description": "Quantity"})
    # Assertion: confirm both type and description are retained.
    assert field_spec.py_type is int
    assert field_spec.constraints["description"] == "Quantity"


def test_field_spec_uses_explicit_constraints_for_descriptions():
    """Demonstrate how to store descriptions in the constraints mapping.

    Purpose: show that field metadata is carried through the ``constraints``
    dictionary, which keeps the API surface explicit and avoids hidden magic.

    Best practice: include user-facing descriptions in the constraints mapping
    so documentation tooling can rely on a single source of truth.
    """
    # Setup: attach a description via the constraints mapping.
    field_spec = F(py_type=str, constraints={"description": "Display name"})
    # Assertion: the description is stored in the constraints mapping.
    assert field_spec.constraints["description"] == "Display name"
