from examples._support import build_constraints, build_widget_model


def test_table_constraints_are_in_metadata():
    """Test table constraints are in metadata."""
    Widget = build_widget_model("LessonTableArgs", with_table_args=build_constraints())
    constraint_names = {constraint.name for constraint in Widget.__table__.constraints}
    assert "ck_widget_name" in constraint_names
