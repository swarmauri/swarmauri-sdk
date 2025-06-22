import pytest
from peagen._utils._graph import (
    get_immediate_dependencies,
    _topological_sort,
    _transitive_dependency_sort,
)

PAYLOAD = [
    {"RENDERED_FILE_NAME": "a", "EXTRAS": {}},
    {"RENDERED_FILE_NAME": "b", "EXTRAS": {"DEPENDENCIES": ["a"]}},
    {"RENDERED_FILE_NAME": "c", "EXTRAS": {"DEPENDENCIES": ["b"]}},
    {"RENDERED_FILE_NAME": "d", "EXTRAS": {"DEPENDENCIES": ["a", "c"]}},
]


@pytest.mark.unit
def test_immediate_dependencies():
    assert get_immediate_dependencies(PAYLOAD, "c") == ["b"]
    with pytest.raises(ValueError):
        get_immediate_dependencies(PAYLOAD, "missing")


@pytest.mark.unit
def test_topological_sort():
    order = [e["RENDERED_FILE_NAME"] for e in _topological_sort(PAYLOAD)]
    assert order == ["a", "b", "c", "d"]


@pytest.mark.unit
def test_transitive_dependency_sort():
    order = [e["RENDERED_FILE_NAME"] for e in _transitive_dependency_sort(PAYLOAD, "d")]
    assert order == ["a", "b", "c", "d"]


@pytest.mark.unit
def test_topological_sort_cycle():
    cycle_payload = [
        {"RENDERED_FILE_NAME": "a", "EXTRAS": {"DEPENDENCIES": ["a"]}},
    ]
    with pytest.raises(ValueError, match="Cyclic dependencies detected"):
        _topological_sort(cycle_payload)


@pytest.mark.unit
def test_topological_sort_two_node_cycle():
    cycle_payload = [
        {"RENDERED_FILE_NAME": "a", "EXTRAS": {"DEPENDENCIES": ["b"]}},
        {"RENDERED_FILE_NAME": "b", "EXTRAS": {"DEPENDENCIES": ["a"]}},
    ]
    with pytest.raises(ValueError, match="Cyclic dependencies detected"):
        _topological_sort(cycle_payload)
