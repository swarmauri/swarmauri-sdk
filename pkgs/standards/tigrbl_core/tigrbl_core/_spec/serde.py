from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from importlib import import_module
from typing import Any, TypeVar

T = TypeVar("T")


def _class_path(value: type) -> str:
    return f"{value.__module__}:{value.__qualname__}"


def _resolve_path(path: str) -> Any:
    module_name, _, qualname = path.partition(":")
    if not module_name or not qualname:
        raise ValueError(f"Invalid import path: {path}")
    value: Any = import_module(module_name)
    for segment in qualname.split("."):
        value = getattr(value, segment)
    return value


def _serialize_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if is_dataclass(value):
        payload = {
            f.name: _serialize_value(getattr(value, f.name)) for f in fields(value)
        }
        payload["__dataclass__"] = _class_path(value.__class__)
        return payload
    if isinstance(value, tuple):
        return {"__tuple__": [_serialize_value(item) for item in value]}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _serialize_value(item) for key, item in value.items()}
    if isinstance(value, type):
        return {"__class__": _class_path(value)}
    if callable(value):
        try:
            return {"__callable__": _class_path(value)}
        except Exception:
            return repr(value)
    return repr(value)


def _deserialize_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_deserialize_value(item) for item in value]
    if isinstance(value, dict):
        if "__tuple__" in value:
            return tuple(_deserialize_value(item) for item in value["__tuple__"])
        if "__class__" in value:
            return _resolve_path(value["__class__"])
        if "__callable__" in value:
            return _resolve_path(value["__callable__"])
        if "__dataclass__" in value:
            cls = _resolve_path(value["__dataclass__"])
            payload = {
                key: _deserialize_value(item)
                for key, item in value.items()
                if key != "__dataclass__"
            }
            return cls(**payload)
        return {key: _deserialize_value(item) for key, item in value.items()}
    return value


def _load_yaml(yaml_str: str) -> Any:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "PyYAML is required for from_yaml(). Install with `pip install pyyaml`."
        ) from exc
    return yaml.safe_load(yaml_str)


def _dump_yaml(value: Any) -> str:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "PyYAML is required for to_yaml(). Install with `pip install pyyaml`."
        ) from exc
    return yaml.safe_dump(value, sort_keys=False)


def _load_toml(toml_str: str) -> Any:
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
        import tomli as tomllib  # type: ignore
    return tomllib.loads(toml_str)


def _dump_toml(value: Any) -> str:
    def _toml_sanitize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                key: _toml_sanitize(item)
                for key, item in obj.items()
                if item is not None
            }
        if isinstance(obj, list):
            return [_toml_sanitize(item) for item in obj if item is not None]
        if isinstance(obj, tuple):
            return tuple(_toml_sanitize(item) for item in obj if item is not None)
        return obj

    value = _toml_sanitize(value)
    try:
        import tomli_w

        return tomli_w.dumps(value)
    except ModuleNotFoundError:
        try:
            import toml

            return toml.dumps(value)
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "tomli-w or toml is required for to_toml(). Install with `pip install tomli-w`."
            ) from exc


class SerdeMixin:
    def to_dict(self) -> dict[str, Any]:
        if is_dataclass(self):
            return {
                field.name: _serialize_value(getattr(self, field.name))
                for field in fields(self)
            }

        return {
            key: _serialize_value(value)
            for key, value in vars(self).items()
            if not key.startswith("_")
        }

    @classmethod
    def from_dict(cls: type[T], payload: dict[str, Any]) -> T:
        restored = {key: _deserialize_value(value) for key, value in payload.items()}
        if is_dataclass(cls):
            valid = {field.name for field in fields(cls)}
            restored = {key: value for key, value in restored.items() if key in valid}
        return cls(**restored)

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_json(cls: type[T], payload: str) -> T:
        return cls.from_dict(json.loads(payload))

    def to_yaml(self) -> str:
        return _dump_yaml(self.to_dict())

    @classmethod
    def from_yaml(cls: type[T], payload: str) -> T:
        data = _load_yaml(payload)
        if not isinstance(data, dict):
            raise TypeError("YAML input must decode to a mapping")
        return cls.from_dict(data)

    def to_toml(self) -> str:
        return _dump_toml(self.to_dict())

    @classmethod
    def from_toml(cls: type[T], payload: str) -> T:
        data = _load_toml(payload)
        if not isinstance(data, dict):
            raise TypeError("TOML input must decode to a mapping")
        return cls.from_dict(data)


__all__ = ["SerdeMixin"]
