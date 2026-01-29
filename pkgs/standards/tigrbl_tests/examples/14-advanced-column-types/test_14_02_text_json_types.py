from __future__ import annotations

from tigrbl.specs import S
from tigrbl.types import DateTime, JSON, TZDateTime, Text


def test_text_json_and_temporal_types() -> None:
    assert S(type_=Text).type_ is Text
    assert S(type_=JSON).type_ is JSON
    assert S(type_=DateTime).type_ is DateTime
    assert S(type_=TZDateTime).type_ is TZDateTime
