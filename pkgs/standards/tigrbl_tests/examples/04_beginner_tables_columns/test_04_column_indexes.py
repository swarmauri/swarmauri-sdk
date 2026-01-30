from tigrbl.types import Index
from examples._support import build_widget_model


def test_index_metadata_registered():
    """Test index metadata registered."""
    Widget = build_widget_model(
        "LessonIndexMeta", with_table_args=[Index("ix_name", "name")]
    )
    assert {idx.name for idx in Widget.__table__.indexes} == {"ix_name"}
