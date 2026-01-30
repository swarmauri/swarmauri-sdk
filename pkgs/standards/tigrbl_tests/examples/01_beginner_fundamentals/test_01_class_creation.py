from examples._support import build_widget_model


def test_class_creation_builds_table_and_columns():
    """Test class creation builds table and columns."""
    Widget = build_widget_model("LessonWidget")
    assert Widget.__tablename__ == "lessonwidgets"
    assert "name" in Widget.__table__.c
