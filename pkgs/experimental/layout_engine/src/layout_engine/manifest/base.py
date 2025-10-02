from __future__ import annotations
from typing import Protocol, Mapping, Any
from .spec import Manifest

class IManifestBuilder(Protocol):
    def build(self, view_model: Mapping[str, Any]) -> Manifest: ...
