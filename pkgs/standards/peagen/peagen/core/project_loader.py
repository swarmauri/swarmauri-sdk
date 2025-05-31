from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml
from colorama import Fore, Style

from .._utils.slug_utils import slugify


class ProjectLoader:
    """Load projects from a YAML payload."""

    def __init__(self, projects_payload_path: str, logger) -> None:
        self.projects_payload_path = projects_payload_path
        self.logger = logger
        self.projects_list: List[Dict[str, Any]] = []
        self.slug_map: Dict[str, str] = {}

    def load_projects(self) -> List[Dict[str, Any]]:
        if self.logger:
            self.logger.debug(f"Loading projects from {self.projects_payload_path}")
        try:
            with open(self.projects_payload_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                self.projects_list = data.get("PROJECTS", [])
            else:
                self.projects_list = data
            self.logger.info(
                "Loaded "
                + Fore.GREEN
                + f"{len(self.projects_list)}"
                + Style.RESET_ALL
                + f" projects from '{self.projects_payload_path}'."
            )
            self.slug_map = {
                slugify(p.get("NAME", "")): p.get("NAME", "")
                for p in self.projects_list
                if p.get("NAME")
            }
        except Exception as e:
            self.logger.error(f"Failed to load projects: {e}")
            self.projects_list = []
        return self.projects_list
