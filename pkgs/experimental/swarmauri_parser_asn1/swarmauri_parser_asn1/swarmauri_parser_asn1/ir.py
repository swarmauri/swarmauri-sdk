from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union, Literal

TagClass = Literal["UNIVERSAL", "APPLICATION", "CONTEXT", "PRIVATE"]

@dataclass
class Tag:
    cls: TagClass
    num: int
    mode: Literal["implicit", "explicit", "none"] = "none"

@dataclass
class Constraint:
    size: Optional[Tuple[int,int]] = None
    value_range: Optional[Tuple[int,int]] = None

@dataclass
class TypeRef:
    name: str

@dataclass
class Builtin:
    kind: str                      # e.g., "INTEGER", "UTF8String", "SEQUENCE", ...
    enum: Optional[Dict[str,int]] = None

@dataclass
class Field:
    name: str
    type: Any
    optional: bool = False
    default: Any = None
    tag: Optional[Tag] = None
    constraint: Optional[Constraint] = None

@dataclass
class Sequence:
    fields: List[Field]

@dataclass
class SetType:
    fields: List[Field]

@dataclass
class SeqOf:
    elem: Any

@dataclass
class SetOf:
    elem: Any

@dataclass
class Choice:
    alts: List[tuple[str, Any]]    # [(altName, type), ...]

TypeNode = Union[Builtin, TypeRef, Sequence, SetType, SeqOf, SetOf, Choice, tuple]

@dataclass
class TypeAssignment:
    name: str
    type: TypeNode

@dataclass
class ValueAssignment:
    name: str
    type: TypeNode
    value: Any

@dataclass
class Module:
    name: str
    types: Dict[str, TypeAssignment] = field(default_factory=dict)
    values: Dict[str, ValueAssignment] = field(default_factory=dict)

@dataclass
class Schema:
    modules: Dict[str, Module] = field(default_factory=dict)

    def resolve(self, name: str) -> TypeNode:
        for m in self.modules.values():
            if name in m.types:
                return m.types[name].type
        raise KeyError(f"Unknown type: {name}")