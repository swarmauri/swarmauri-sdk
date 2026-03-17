from __future__ import annotations

from types import SimpleNamespace

from tigrbl_concrete._mapping.router.common import AttrDict


def test_attrdict_and_simplenamespace_similarity_attribute_reads() -> None:
    attrs = AttrDict()
    attrs.widget = 1

    ns = SimpleNamespace(widget=1)

    assert attrs.widget == ns.widget == 1


def test_attrdict_and_simplenamespace_differences_mapping_behavior() -> None:
    attrs = AttrDict()
    attrs["widget"] = 1

    ns = SimpleNamespace(widget=1)

    assert attrs["widget"] == 1
    assert "widget" in attrs

    try:
        _ = ns["widget"]  # type: ignore[index]
        raised = False
    except TypeError:
        raised = True

    assert raised is True
