import pytest
from peagen.core.sort_core import sort_file_records


@pytest.mark.unit
def test_sort_file_records_basic_order():
    records = [
        {"RENDERED_FILE_NAME": "a.txt", "EXTRAS": {}},
        {"RENDERED_FILE_NAME": "b.txt", "EXTRAS": {"DEPENDENCIES": ["a.txt"]}},
    ]
    sorted_recs, next_idx = sort_file_records(file_records=records)
    assert [r["RENDERED_FILE_NAME"] for r in sorted_recs] == ["a.txt", "b.txt"]
    assert next_idx == 2


@pytest.mark.unit
def test_sort_file_records_transitive():
    records = [
        {"RENDERED_FILE_NAME": "a.txt", "EXTRAS": {}},
        {"RENDERED_FILE_NAME": "b.txt", "EXTRAS": {"DEPENDENCIES": ["a.txt"]}},
        {"RENDERED_FILE_NAME": "c.txt", "EXTRAS": {"DEPENDENCIES": ["b.txt"]}},
    ]
    sorted_recs, _ = sort_file_records(
        file_records=records,
        start_file="c.txt",
        transitive=True,
    )
    assert [r["RENDERED_FILE_NAME"] for r in sorted_recs] == [
        "a.txt",
        "b.txt",
        "c.txt",
    ]
