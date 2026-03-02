from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Callable, Dict, Mapping, Tuple


_ROUTE_SEGMENT_RE = re.compile(r"^\{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\}$")


class RestRouteIndex(dict[str, int]):
    """REST selector index with ``match(method, path)`` compatibility API."""

    def __call__(self, method: str, path: str) -> tuple[int, dict[str, str]]:
        return self.match(method, path)

    def match(self, method: str, path: str) -> tuple[int, dict[str, str]]:
        normalized_method = (method or "").upper()
        normalized_path = self._normalize_path(path)
        selector = f"{normalized_method} {normalized_path}"

        exact = self.get(selector)
        if isinstance(exact, int):
            return exact, {}

        path_parts = self._split_path(normalized_path)
        for candidate, meta_index in self.items():
            try:
                cand_method, cand_path = candidate.split(" ", 1)
            except ValueError:
                continue
            if cand_method != normalized_method:
                continue

            params = self._match_template(cand_path, path_parts)
            if params is not None:
                return meta_index, params

        raise KeyError(selector)

    @staticmethod
    def _normalize_path(path: str) -> str:
        text = (path or "").strip()
        if not text:
            return "/"
        if not text.startswith("/"):
            text = f"/{text}"
        return text.rstrip("/") or "/"

    @staticmethod
    def _split_path(path: str) -> tuple[str, ...]:
        if path == "/":
            return ()
        return tuple(segment for segment in path.split("/") if segment)

    @classmethod
    def _match_template(
        cls, template_path: str, actual_parts: tuple[str, ...]
    ) -> dict[str, str] | None:
        template_parts = cls._split_path(cls._normalize_path(template_path))
        if len(template_parts) != len(actual_parts):
            return None

        out: dict[str, str] = {}
        for template_part, actual_part in zip(template_parts, actual_parts):
            matched = _ROUTE_SEGMENT_RE.match(template_part)
            if matched:
                out[matched.group("name")] = actual_part
                continue
            if template_part != actual_part:
                return None
        return out


@dataclass(frozen=True)
class SchemaIn:
    fields: Tuple[str, ...]
    by_field: Dict[str, Dict[str, object]]


@dataclass(frozen=True)
class SchemaOut:
    fields: Tuple[str, ...]
    by_field: Dict[str, Dict[str, object]]
    expose: Tuple[str, ...]


@dataclass(frozen=True)
class OpView:
    schema_in: SchemaIn
    schema_out: SchemaOut
    paired_index: Dict[str, Dict[str, object]]
    virtual_producers: Dict[str, Callable[[object, dict], object]]
    to_stored_transforms: Dict[str, Callable[[object, dict], object]]
    refresh_hints: Tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OpKey:
    proto: str
    selector: str


@dataclass(frozen=True, slots=True)
class OpMeta:
    model: type
    alias: str
    target: str


@dataclass(frozen=True, slots=True)
class KernelPlan:
    proto_indices: Mapping[str, Any] = field(default_factory=dict)
    opmeta: tuple[OpMeta, ...] = ()
    opkey_to_meta: Mapping[OpKey, int] = field(default_factory=dict)
    ingress_chain: Mapping[str, list[Callable[..., Any]]] = field(default_factory=dict)
    phase_chains: Mapping[int, Mapping[str, list[Callable[..., Any]]]] = field(
        default_factory=dict
    )
    egress_chain: Mapping[str, list[Callable[..., Any]]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        rest_index = self.proto_indices.get("http.rest")
        if isinstance(rest_index, dict) and not isinstance(rest_index, RestRouteIndex):
            normalized = dict(self.proto_indices)
            normalized["http.rest"] = RestRouteIndex(rest_index)
            object.__setattr__(self, "proto_indices", normalized)

    def _legacy_payload(self) -> dict[str, dict[str, list[str]]]:
        payload: dict[str, dict[str, list[str]]] = {}
        for index, meta in enumerate(self.opmeta):
            chains = self.phase_chains.get(index, {})
            sequence: list[str] = []
            for phase, steps in chains.items():
                for step in steps or ():
                    label = getattr(step, "__tigrbl_label", None)
                    if isinstance(label, str):
                        entry = label
                    else:
                        name = getattr(
                            step, "__qualname__", getattr(step, "__name__", repr(step))
                        )
                        module = getattr(step, "__module__", None)
                        subject = f"{module}.{name}" if module else name
                        entry = f"hook:wire:{subject.replace('.', ':')}@{phase}"
                    sequence.append(f"{phase}:{entry}")
            model_name = getattr(meta.model, "__name__", "Model")
            payload.setdefault(model_name, {})[meta.alias] = sequence
        return payload

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, str) and hasattr(self, key):
            return getattr(self, key)
        return self._legacy_payload()[key]
