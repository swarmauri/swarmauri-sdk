# File: peagen/doe.py
"""Design of Experiments helpers."""

import copy
import itertools
from pathlib import Path
from typing import Any, Dict

import yaml
from jinja2 import Template
import jsonpatch


class DOEManager:
    """
    Manager for Design of Experiments (DOE) integration within Peagen.
    """

    def __init__(self, spec_path: str, template_path: str):
        """
        DOEManager.__init__
        :param spec_path: path to the doe_spec.yaml file
        :param template_path: path to the template_project.yaml file
        """
        self.spec_path = Path(spec_path)
        self.template_path = Path(template_path)
        self.spec: Dict[str, Any] = {}
        self.base_project: Dict[str, Any] = {}
        self.payloads: list[Dict[str, Any]] = []

    def load_spec(self) -> None:
        """
        DOEManager.load_spec
        Loads the DOE spec (with factors) and the base project template.
        """
        doc = yaml.safe_load(self.spec_path.read_text(encoding="utf-8"))
        self.spec = doc.get("factors", {})
        tmpl = yaml.safe_load(self.template_path.read_text(encoding="utf-8"))
        projects = tmpl.get("PROJECTS", [])
        if not projects:
            raise ValueError(
                "template_project.yaml must contain a top-level 'PROJECTS' list"
            )
        self.base_project = projects[0]

    def build_designs(self) -> list[Dict[str, Any]]:
        """
        DOEManager.build_designs
        Computes the Cartesian product of all factor levels.
        Now uses each factor's `code` as the key, so Jinja sees CMP rather than COMPONENT.
        """
        codes = []
        level_lists = []
        for factor in self.spec.values():
            codes.append(factor["code"])
            level_lists.append(factor["levels"])

        # Each design is { "CMP": {...}, ... }
        return [dict(zip(codes, combo)) for combo in itertools.product(*level_lists)]

    def _get_from_context(self, expr: str, ctx: Dict[str, Any]) -> Any:
        """
        DOEManager._get_from_context
        Fetches a nested property from ctx given 'A.B.C' notation.
        """
        val = ctx
        for part in expr.split("."):
            val = val[part]
        return val

    def render_patches(
        self, design: Dict[str, Any], exp_id: str
    ) -> list[Dict[str, Any]]:
        """
        DOEManager.render_patches
        Renders JSON-Patch operations for a single design.
        """
        ctx = {**design, "EXP_ID": exp_id, "BASE_NAME": self.base_project.get("NAME")}
        patches: list[Dict[str, Any]] = []

        for factor in self.spec.values():
            for pt in factor.get("patches", []):
                raw_val = pt["value"]

                # SPECIAL CASE: single-key mapping like { "CMP.requirements": null }
                if isinstance(raw_val, dict) and len(raw_val) == 1:
                    key = next(iter(raw_val))
                    if "." in key:
                        val = self._get_from_context(key, ctx)
                        patches.append(
                            {"op": pt["op"], "path": pt["path"], "value": val}
                        )
                        continue

                # GENERAL CASE: render the template string directly
                rendered = Template(str(raw_val)).render(**ctx)
                val = yaml.safe_load(rendered)

                patches.append({"op": pt["op"], "path": pt["path"], "value": val})

        return patches

    def generate(self) -> list[Dict[str, Any]]:
        """
        DOEManager.generate
        Orchestrates loading, design building, patch rendering, and JSON-patch application.
        Populates and returns self.payloads.
        """
        self.load_spec()
        designs = self.build_designs()

        for idx, design in enumerate(designs, start=1):
            exp_id = f"{idx:03d}"
            patches = self.render_patches(design, exp_id)

            # wrap under PROJECTS to match JSON-Patch paths
            wrapper = {"PROJECTS": [copy.deepcopy(self.base_project)]}
            result = jsonpatch.apply_patch(wrapper, patches, in_place=False)

            project = result["PROJECTS"][0]
            project["EXPERIMENT"] = {"FACTORS": design}
            self.payloads.append(project)

        return self.payloads

    def write_payloads(self, output_path: str) -> None:
        """
        DOEManager.write_payloads
        Writes the generated PROJECTS list to a YAML file at output_path.
        """
        out = {"PROJECTS": self.payloads}
        Path(output_path).write_text(yaml.safe_dump(out), encoding="utf-8")
