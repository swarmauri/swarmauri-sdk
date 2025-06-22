from __future__ import annotations

from typing import List, Optional, Literal, Any
import requests
import yaml
from pydantic import Field, PrivateAttr

from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import DynamicBase
from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "GithubLoadedTool")
class GithubLoadedTool(ToolBase):
    """Load a component definition from a GitHub-hosted YAML file."""

    version: str = "0.1.0"

    owner: str
    repo: str
    path: str
    branch: str = "main"
    commit_ref: Optional[str] = None
    token: Optional[str] = None
    use_cache: bool = True

    name: str = "GithubLoadedTool"
    description: Optional[str] = "Load a component from GitHub"
    parameters: List[Parameter] = Field(default_factory=list)
    type: Literal["GithubLoadedTool"] = "GithubLoadedTool"

    _component: Optional[ComponentBase] = PrivateAttr(default=None)

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.use_cache:
            try:
                self._load_component()
            except Exception:
                self._component = None

    def _ref(self) -> str:
        return self.commit_ref or self.branch

    def _fetch_yaml(self) -> str:
        url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self._ref()}/{self.path}"
        headers = {"Authorization": f"token {self.token}"} if self.token else {}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text

    def _load_component(self) -> ComponentBase:
        if self.use_cache and self._component is not None:
            return self._component

        yaml_text = self._fetch_yaml()
        try:
            parsed = yaml.safe_load(yaml_text)
            component_type = parsed.get("type")
            if component_type:
                registry = DynamicBase._registry.get("ToolBase", {})
                component_cls = registry.get("subtypes", {}).get(component_type)
                if component_cls:
                    component = component_cls.model_validate_yaml(yaml_text)
                else:
                    component = ComponentBase.model_validate_yaml(yaml_text)
            else:
                component = ComponentBase.model_validate_yaml(yaml_text)
        except Exception:
            component = ComponentBase.model_validate_yaml(yaml_text)
        self._component = component

        if getattr(component, "name", None):
            self.name = component.name  # type: ignore[assignment]
        if hasattr(component, "description"):
            self.description = getattr(component, "description")
        if hasattr(component, "parameters"):
            self.parameters = getattr(component, "parameters")  # type: ignore[assignment]

        return component

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        component = self._load_component()
        return component(*args, **kwargs)
