from tigrbl.column import F


def test_field_spec_defaults_and_constraints():
    spec = F(py_type=str, constraints={"min_length": 2}, required_in=("create",))
    assert spec.py_type is str
    assert spec.constraints["min_length"] == 2
    assert spec.required_in == ("create",)
    assert spec.allow_null_in == ()


def test_field_spec_constraints_are_isolated():
    first = F()
    second = F()
    first.constraints["max_length"] = 10
    assert "max_length" not in second.constraints
