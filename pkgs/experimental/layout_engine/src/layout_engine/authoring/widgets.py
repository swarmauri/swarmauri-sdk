from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class _Base:
    id: str
    role: str
    props: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Text(_Base):
    def __init__(self, id: str, value: str = "", **props):
        super().__init__(id=id, role="text", props={"value": value, **props})

@dataclass
class Button(_Base):
    def __init__(self, id: str, label: str = "Run", **props):
        super().__init__(id=id, role="button", props={"label": label, **props})

@dataclass
class Timeseries(_Base):
    def __init__(self, id: str, series: list[dict] | None = None, **props):
        super().__init__(id=id, role="timeseries", props={"series": series or [], **props})
