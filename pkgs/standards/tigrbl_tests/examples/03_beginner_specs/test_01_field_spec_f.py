from tigrbl.specs import F


def test_field_spec_describes_python_type():
    """Test field spec describes python type."""
    field_spec = F(py_type=int, constraints={"description": "Quantity"})
    assert field_spec.py_type is int
    assert field_spec.constraints["description"] == "Quantity"
