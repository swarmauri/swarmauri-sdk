from tigrbl.types import Index
from examples._support import build_widget_model


def test_table_args_support_indexes():
    Widget = build_widget_model(
        "LessonIndex", with_table_args=[Index("ix_widget_name", "name")]
    )
    index_names = {index.name for index in Widget.__table__.indexes}
    assert "ix_widget_name" in index_names
