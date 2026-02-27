# tigrbl/v3/ops/types.py
from __future__ import annotations

from typing import Tuple, cast, Literal

from ..config.constants import CANON as CANONICAL_VERB_TUPLE
from .._spec.op_spec import Arity, OpSpec, PersistPolicy, TargetOp

VerbAliasPolicy = Literal["both", "alias_only", "canonical_only"]  # legacy export

# Canonical verb set
CANON: Tuple[TargetOp, ...] = cast(Tuple[TargetOp, ...], CANONICAL_VERB_TUPLE)

__all__ = [
    "PersistPolicy",
    "Arity",
    "TargetOp",
    "VerbAliasPolicy",
    "OpSpec",
    "CANON",
]
