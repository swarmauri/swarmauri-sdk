from examples._support import build_constraints, build_widget_model


def test_table_args_register_constraints():
    Widget = build_widget_model(
        "LessonConstraints", with_table_args=build_constraints()
    )
    constraint_names = {constraint.name for constraint in Widget.__table__.constraints}
    assert "uq_widget_name" in constraint_names
    assert "ck_widget_name" in constraint_names
