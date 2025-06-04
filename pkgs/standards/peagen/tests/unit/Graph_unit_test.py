import pytest

from peagen._utils._graph import (
    _topological_sort,
    _transitive_dependency_sort,
    get_immediate_dependencies,
)


@pytest.mark.unit
def test_topological_sort_basic():
    payload = [
        {"RENDERED_FILE_NAME": "a", "EXTRAS": {"DEPENDENCIES": []}},
        {"RENDERED_FILE_NAME": "b", "EXTRAS": {"DEPENDENCIES": ["a"]}},
        {"RENDERED_FILE_NAME": "c", "EXTRAS": {"DEPENDENCIES": ["b"]}},
    ]
    sorted_records = _topological_sort(payload)
    assert [r["RENDERED_FILE_NAME"] for r in sorted_records] == ["a", "b", "c"]


@pytest.mark.unit
def test_transitive_dependency_sort():
    payload = [
        {"RENDERED_FILE_NAME": "a", "EXTRAS": {"DEPENDENCIES": []}},
        {"RENDERED_FILE_NAME": "b", "EXTRAS": {"DEPENDENCIES": ["a"]}},
        {"RENDERED_FILE_NAME": "c", "EXTRAS": {"DEPENDENCIES": ["b"]}},
        {"RENDERED_FILE_NAME": "d", "EXTRAS": {"DEPENDENCIES": []}},
    ]
    sorted_records = _transitive_dependency_sort(payload, "c")
    assert [r["RENDERED_FILE_NAME"] for r in sorted_records] == ["a", "b", "c"]


@pytest.mark.unit
def test_get_immediate_dependencies():
    payload = [
        {"RENDERED_FILE_NAME": "a", "EXTRAS": {"DEPENDENCIES": []}},
        {"RENDERED_FILE_NAME": "b", "EXTRAS": {"DEPENDENCIES": ["a"]}},
        {"RENDERED_FILE_NAME": "c", "EXTRAS": {"DEPENDENCIES": ["b"]}},
    ]
    deps = get_immediate_dependencies(payload, "c")
    assert deps == ["b"]
