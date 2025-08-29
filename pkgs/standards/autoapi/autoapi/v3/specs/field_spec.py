# field_spec.py
from __future__ import annotations
from dataclasses import dataclass, field as dc_field
from typing import Any, Dict, Tuple, Callable
from pydantic import ValidationInfo  # v2

PreFn = Callable[[Any, ValidationInfo], Any]  # BeforeValidator
PostFn = Callable[[Any, ValidationInfo], Any]  # AfterValidator


@dataclass(frozen=True)
class FieldSpec:
    """
    - py_type may be omitted when annotated on the model; we infer it.
    - No custom serializers: responses use Pydantic BaseModel's built-in encoders based on type.
    """

    py_type: Any = Any

    # For request/response schema generation (+ pydantic.Field)
    constraints: Dict[str, Any] = dc_field(default_factory=dict)

    # Request policy (DB nullability lives in StorageSpec.nullable)
    required_in: Tuple[str, ...] = ()
    allow_null_in: Tuple[str, ...] = ()
