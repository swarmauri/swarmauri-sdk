# field_spec.py
from __future__ import annotations
from dataclasses import dataclass, field as dc_field
from typing import Any, Dict, Tuple, Callable
from pydantic import ValidationInfo  # v2

PreFn = Callable[[Any, ValidationInfo], Any]  # BeforeValidator
PostFn = Callable[[Any, ValidationInfo], Any]  # AfterValidator


@dataclass(frozen=True)
class FieldSpec:
    """Describe Python-side metadata for a column or virtual field.

    ``py_type`` denotes the expected Python type and may be omitted when the
    model attribute is annotated; the type will then be inferred. ``constraints``
    mirrors arguments accepted by :func:`pydantic.Field` and participates in
    schema generation. ``description`` provides a convenience field for schema
    metadata. ``required_in`` and ``allow_null_in`` govern which API verbs must
    supply the value or may explicitly send ``null`` in requests. Responses rely
    on Pydantic's built-in encoders based solely on the declared type.
    """

    py_type: Any = Any

    # For request/response schema generation (+ pydantic.Field)
    constraints: Dict[str, Any] = dc_field(default_factory=dict)
    description: str | None = None

    # Request policy (DB nullability lives in StorageSpec.nullable)
    required_in: Tuple[str, ...] = ()
    allow_null_in: Tuple[str, ...] = ()
