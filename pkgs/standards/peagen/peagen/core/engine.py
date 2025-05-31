"""Peagen orchestration engine composed of smaller helpers."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from colorama import Fore, Style
from colorama import init as colorama_init
from pydantic import ConfigDict, Field, model_validator
from swarmauri_base import SubclassUnion
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.loggers.LoggerBase import LoggerBase
from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

from swarmauri_standard.loggers.Logger import Logger

from .._config import __logger_name__, __version__
from .project_loader import ProjectLoader
from .project_processor import ProjectProcessor
from .template_manager import TemplateManager

colorama_init(autoreset=True)


class Peagen(ComponentBase):
    """Encapsulates payload → file-generation workflow using composition."""

    projects_payload_path: str
    org: Optional[str] = None

    storage_adapter: Optional[Any] = Field(default=None, exclude=True)
    agent_env: Dict[str, Any] = Field(default_factory=dict)
    j2pt: Any = Field(default_factory=lambda: J2PromptTemplate())

    cwd: str = Field(exclude=True, default_factory=os.getcwd)

    workspace_root: Optional[Path] = Field(
        default=None,
        exclude=True,
        description="Workspace where generated & copied files live.",
    )

    source_packages: List[Dict[str, Any]] = Field(default_factory=list)
    template_sets: List[Dict[str, Any]] = Field(default_factory=list)

    logger: SubclassUnion["LoggerBase"] = Logger(
        name=Fore.GREEN + __logger_name__ + Style.RESET_ALL
    )
    dry_run: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)
    version: str = __version__

    _template_manager: TemplateManager | None = Field(default=None, exclude=True)
    _loader: ProjectLoader | None = Field(default=None, exclude=True)
    _processor: ProjectProcessor | None = Field(default=None, exclude=True)

    slug_map: Dict[str, str] = Field(default_factory=dict, exclude=True)

    @model_validator(mode="after")
    def _setup_components(self) -> "Peagen":
        self._template_manager = TemplateManager(
            j2pt=self.j2pt,
            cwd=self.cwd,
            workspace_root=self.workspace_root,
            source_packages=self.source_packages,
            logger=self.logger,
        )
        self._loader = ProjectLoader(self.projects_payload_path, self.logger)
        self._processor = ProjectProcessor(
            template_manager=self._template_manager,
            j2pt=self.j2pt,
            agent_env=self.agent_env,
            logger=self.logger,
            storage_adapter=self.storage_adapter,
            org=self.org,
            workspace_root=self.workspace_root,
            source_packages=self.source_packages,
            template_sets=self.template_sets,
            dry_run=self.dry_run,
        )
        return self

    # Public API delegates to composed helpers ---------------------------
    def update_templates_dir(self, package_specific_template_dir: str | Path) -> None:
        self._template_manager.update_templates_dir(package_specific_template_dir)

    def locate_template_set(self, template_set: str) -> Path:
        return self._template_manager.locate_template_set(template_set)

    def load_projects(self) -> List[Dict[str, Any]]:
        projects = self._loader.load_projects()
        self.slug_map.update(self._loader.slug_map)
        return projects

    def process_all_projects(self) -> list:
        if not self._loader.projects_list:
            self.load_projects()
        result = self._processor.process_all_projects(self._loader.projects_list)
        self.slug_map.update(self._processor.slug_map)
        return result

    def process_single_project(
        self,
        project: Dict[str, Any],
        start_idx: int = 0,
        start_file: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        records = self._processor.process_single_project(project, start_idx, start_file)
        self.slug_map.update(self._processor.slug_map)
        return records
