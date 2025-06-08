import httpx
import yaml
from typing import Dict, List, Optional, Any, Literal
from pydantic import Field, PrivateAttr, TypeAdapter
from importlib import import_module

from swarmauri_base import SubclassUnion

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "HTTPLoadedTool")
class HTTPLoadedTool(ToolBase):
    """Load components from a remote YAML manifest when instantiated."""

    name: str = "HTTPLoadedTool"
    description: str = "Load components from a remote YAML manifest"
    type: Literal["HTTPLoadedTool"] = "HTTPLoadedTool"
    parameters: List[Parameter] = Field(default_factory=list)

    url: str
    headers: Optional[Dict[str, str]] = None
    use_cache: bool = True

    _cache: Dict[str, str] = PrivateAttr(default_factory=dict)
    _manifest: Dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None, use_cache: bool = True, **data: Any) -> None:
        super().__init__(url=url, headers=headers, use_cache=use_cache, **data)
        self.url = url
        self.headers = headers
        self.use_cache = use_cache
        self._load_manifest()

    def _load_manifest(self) -> None:
        if self.use_cache and self.url in self._cache:
            yaml_text = self._cache[self.url]
        else:
            response = httpx.get(self.url, headers=self.headers)
            response.raise_for_status()
            yaml_text = response.text
            if self.use_cache:
                self._cache[self.url] = yaml_text

        try:
            manifest = yaml.safe_load(yaml_text) or {}
        except yaml.YAMLError as exc:  # pragma: no cover - invalid YAML
            raise ValueError(f"Invalid YAML manifest: {exc}") from exc

        self._manifest = manifest if isinstance(manifest, dict) else {}
        self.name = self._manifest.get("name", self.name)
        self.description = self._manifest.get("description", self.description)

        params_data = self._manifest.get("parameters") or []
        if isinstance(params_data, list):
            self.parameters = [
                Parameter.model_validate_yaml(yaml.dump(p)) if not isinstance(p, Parameter) else p
                for p in params_data
                if isinstance(p, (dict, Parameter))
            ]

    def __call__(self) -> List[ComponentBase]:
        components_data = self._manifest.get("components", [])
        if not isinstance(components_data, list):
            components_data = [components_data]

        loaded_components: List[ComponentBase] = []
        for entry in components_data:
            if not isinstance(entry, dict):
                raise ValueError("Each component entry must be a mapping")

            comp_type = entry.get("type")
            if isinstance(comp_type, str):
                try:
                    import_module(f"swarmauri_standard.tools.{comp_type}")
                except Exception:  # pragma: no cover - optional import failure
                    pass
            adapter = TypeAdapter(SubclassUnion[ToolBase])
            loaded_components.append(adapter.validate_python(entry))
        return loaded_components
