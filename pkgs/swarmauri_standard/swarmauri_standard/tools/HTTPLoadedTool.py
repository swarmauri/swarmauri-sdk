import httpx
import yaml
from typing import Dict, List, Optional, Literal
from pydantic import Field, PrivateAttr

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "HTTPLoadedTool")
class HTTPLoadedTool(ToolBase):
    """Load components from a remote YAML manifest."""

    url: str = Field(..., description="HTTP(S) URL of the YAML manifest")
    headers: Optional[Dict[str, str]] = Field(
        default=None, description="Optional HTTP headers"
    )
    use_cache: bool = Field(True, description="Use cached manifest if available")

    name: str = "HTTPLoadedTool"
    description: Optional[str] = "Load components from a remote YAML manifest"
    parameters: List[Parameter] = Field(default_factory=list)
    type: Literal["HTTPLoadedTool"] = "HTTPLoadedTool"

    _cache: Dict[str, str] = PrivateAttr(default_factory=dict)
    _components_data: List[Dict[str, object]] = PrivateAttr(default_factory=list)

    def __init__(self, **data: object) -> None:
        """Initialise the tool and load manifest metadata."""
        super().__init__(**data)
        self._load_manifest()

    def _fetch_manifest(self) -> str:
        if self.use_cache and self.url in self._cache:
            return self._cache[self.url]
        response = httpx.get(self.url, headers=self.headers)
        response.raise_for_status()
        yaml_text = response.text
        if self.use_cache:
            self._cache[self.url] = yaml_text
        return yaml_text

    def _load_manifest(self) -> None:
        yaml_text = self._fetch_manifest()
        try:
            manifest = yaml.safe_load(yaml_text) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML manifest: {exc}") from exc

        if isinstance(manifest, dict):
            self.name = manifest.get("name", self.name)
            self.description = manifest.get("description", self.description)
            if "parameters" in manifest:
                params = manifest.get("parameters") or []
                if not isinstance(params, list):
                    raise ValueError("'parameters' must be a list")
                self.parameters = [Parameter.model_validate(p) for p in params]
            components_data = manifest.get("components", manifest)
        else:
            components_data = manifest

        if not isinstance(components_data, list):
            components_data = [components_data]
        self._components_data = components_data

    def __call__(self) -> List[ComponentBase]:
        """Instantiate components defined in the manifest."""
        loaded_components: List[ComponentBase] = []
        for entry in self._components_data:
            if not isinstance(entry, dict):
                raise ValueError("Each component entry must be a mapping")
            comp_yaml = yaml.dump(entry)
            loaded_components.append(ComponentBase.model_validate_yaml(comp_yaml))

        return loaded_components
