from __future__ import annotations
from abc import ABC, abstractmethod, Mapping, Any
from .spec import Manifest

class IManifestBuilder(ABC):
    @abstractmethod
    def build(self, view_model: Mapping[str, Any]) -> Manifest:
        """Transform a page/site view-model into a render Manifest."""
        raise NotImplementedError
