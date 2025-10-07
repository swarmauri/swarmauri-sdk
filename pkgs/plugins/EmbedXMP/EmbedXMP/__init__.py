"""Dynamic EmbedXMP manager for Swarmauri handlers."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Iterable, List, Sequence, Type

from swarmauri_base.DynamicBase import DynamicBase
from swarmauri_base.xmp import EmbedXmpBase


def _resolve_path(path: str | None, hint: str | None) -> str | None:
    """Return the preferred path value, validating conflicting inputs."""

    if hint is None:
        return path
    if path is None or path == hint:
        return hint
    raise ValueError(
        "conflicting path and hint values supplied; they must match if both are provided"
    )


class EmbedXMP(EmbedXmpBase):
    """Discover and delegate to registered :class:`EmbedXmpBase` handlers."""

    def __init__(
        self,
        handlers: Iterable[Type[EmbedXmpBase]] | None = None,
        *,
        eager_import: bool = True,
    ) -> None:
        super().__init__()
        if eager_import:
            self._import_known_packages()
        self._handlers: List[EmbedXmpBase] = []
        self.refresh(handlers)

    def _import_known_packages(self) -> None:
        for _finder, name, ispkg in pkgutil.iter_modules():
            if not ispkg or not name.startswith("swarmauri_xmp_"):
                continue
            importlib.import_module(name)

    def _registry_classes(self) -> List[Type[EmbedXmpBase]]:
        entry = DynamicBase._registry.get("EmbedXmpBase")
        if not entry:
            return []
        subtypes = entry.get("subtypes", {})
        classes = [cls for cls in subtypes.values() if cls is not EmbedXMP]
        return sorted(classes, key=lambda cls: cls.__name__)

    def refresh(self, handlers: Iterable[Type[EmbedXmpBase]] | None = None) -> None:
        classes: Sequence[Type[EmbedXmpBase]]
        if handlers is None:
            classes = self._registry_classes()
        else:
            classes = list(handlers)
        self._handlers = [cls() for cls in classes]

    def supports(self, header: bytes, path: str = "") -> bool:
        return any(
            self._supports_handler(handler, header, path) for handler in self._handlers
        )

    def _supports_handler(
        self, handler: EmbedXmpBase, header: bytes, path: str
    ) -> bool:
        try:
            return handler.supports(header, path)
        except Exception:
            return False

    def _select(self, data: bytes, path: str | None) -> EmbedXmpBase:
        header = data[:16]
        path_value = path or ""
        for handler in self._handlers:
            if self._supports_handler(handler, header, path_value):
                return handler
        raise ValueError("No XMP handler available for this payload")

    def write_xmp(
        self,
        data: bytes,
        xmp_xml: str,
        path: str | None = None,
        *,
        hint: str | None = None,
    ) -> bytes:
        handler = self._select(data, _resolve_path(path, hint))
        return handler.write_xmp(data, xmp_xml)

    def read_xmp(
        self, data: bytes, path: str | None = None, *, hint: str | None = None
    ) -> str | None:
        handler = self._select(data, _resolve_path(path, hint))
        return handler.read_xmp(data)

    def remove_xmp(
        self, data: bytes, path: str | None = None, *, hint: str | None = None
    ) -> bytes:
        handler = self._select(data, _resolve_path(path, hint))
        return handler.remove_xmp(data)

    def embed(
        self,
        data: bytes,
        xmp_xml: str,
        path: str | None = None,
        *,
        hint: str | None = None,
    ) -> bytes:
        """Alias for :meth:`write_xmp` with optional path ``hint``."""

        return self.write_xmp(data, xmp_xml, path, hint=hint)

    def read(
        self, data: bytes, path: str | None = None, *, hint: str | None = None
    ) -> str | None:
        """Alias for :meth:`read_xmp` with optional path ``hint``."""

        return self.read_xmp(data, path, hint=hint)

    def remove(
        self, data: bytes, path: str | None = None, *, hint: str | None = None
    ) -> bytes:
        """Alias for :meth:`remove_xmp` with optional path ``hint``."""

        return self.remove_xmp(data, path, hint=hint)


_default_embed: EmbedXMP | None = None


def _get_default() -> EmbedXMP:
    global _default_embed
    if _default_embed is None:
        _default_embed = EmbedXMP()
    return _default_embed


def embed(
    data: bytes,
    xmp_xml: str,
    path: str | None = None,
    *,
    hint: str | None = None,
) -> bytes:
    """Embed an XMP packet using the first matching handler.

    Either ``path`` or ``hint`` can be supplied to help the manager select the
    appropriate handler. When both are provided they must match.
    """

    return _get_default().write_xmp(data, xmp_xml, _resolve_path(path, hint))


def read(
    data: bytes,
    path: str | None = None,
    *,
    hint: str | None = None,
) -> str | None:
    """Read an XMP packet using the discovered handlers.

    Either ``path`` or ``hint`` can be supplied to help the manager select the
    appropriate handler. When both are provided they must match.
    """

    return _get_default().read_xmp(data, _resolve_path(path, hint))


def remove(
    data: bytes,
    path: str | None = None,
    *,
    hint: str | None = None,
) -> bytes:
    """Remove an XMP packet via the discovered handlers.

    Either ``path`` or ``hint`` can be supplied to help the manager select the
    appropriate handler. When both are provided they must match.
    """

    return _get_default().remove_xmp(data, _resolve_path(path, hint))


def embed_file(path: str | Path, xmp_xml: str) -> bytes:
    """Embed XMP into ``path`` and overwrite the file."""

    file_path = Path(path)
    result = embed(file_path.read_bytes(), xmp_xml, str(file_path))
    file_path.write_bytes(result)
    return result


def read_file_xmp(path: str | Path) -> str | None:
    """Read XMP from ``path`` if available."""

    file_path = Path(path)
    return read(file_path.read_bytes(), str(file_path))


def remove_file_xmp(path: str | Path) -> bytes:
    """Remove XMP from ``path`` and overwrite the file."""

    file_path = Path(path)
    result = remove(file_path.read_bytes(), str(file_path))
    file_path.write_bytes(result)
    return result


__all__ = [
    "EmbedXMP",
    "embed",
    "read",
    "remove",
    "embed_file",
    "read_file_xmp",
    "remove_file_xmp",
]
