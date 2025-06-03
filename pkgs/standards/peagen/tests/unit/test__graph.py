import random; random.seed(0xA11A)
import pytest
from peagen._graph import (
    _build_forward_graph,
    _topological_sort,
    _transitive_dependency_sort,
    get_immediate_dependencies,
)


def _payload():
    return [
        {
            "RENDERED_FILE_NAME": "A",
            "EXTRAS": {"DEPENDENCIES": ["B"]},
        },
        {
            "RENDERED_FILE_NAME": "B",
            "EXTRAS": {"DEPENDENCIES": []},
        },
        {"RENDERED_FILE_NAME": "C", "EXTRAS": {}},
    ]


@pytest.mark.unit
def test_build_graph():
    g, indeg, nodes = _build_forward_graph(_payload())
    assert g["B"] == ["A"]
    assert indeg["A"] == 1
    assert "C" in nodes


@pytest.mark.unit
def test_topological_sort():
    res = _topological_sort(_payload())
    names = [r["RENDERED_FILE_NAME"] for r in res]
    assert names == ["B", "A", "C"]


@pytest.mark.unit
def test_transitive_sort():
    res = _transitive_dependency_sort(_payload(), "A")
    names = [r["RENDERED_FILE_NAME"] for r in res]
    assert names == ["B", "A"]
    with pytest.raises(ValueError):
        _transitive_dependency_sort(_payload(), "Z")


@pytest.mark.unit
def test_get_immediate_dependencies():
    deps = get_immediate_dependencies(_payload(), "A")
    assert deps == ["B"]
    with pytest.raises(ValueError):
        get_immediate_dependencies(_payload(), "Z")
