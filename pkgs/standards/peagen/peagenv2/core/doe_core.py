# peagen/core/doe_core.py

import itertools
import jsonpatch
import yaml

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Union


def _get_from_context(expr: str, ctx: Dict[str, Any]) -> Any:
    """
    Fetch nested values from ctx given a dotted expression like 'A.B.C'.
    """
    val = ctx
    for part in expr.split("."):
        val = val[part]
    return val


def _load_yaml(source: Union[str, Dict[str, Any], List[Any]]) -> Any:
    """
    If `source` is a dict or list, return it directly.
    If it's a string and corresponds to a file path, load that YAML and return.
    Otherwise, raise FileNotFoundError.
    """
    if isinstance(source, (dict, list)):
        return source
    path = Path(source)
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Could not find or parse YAML from {source!r}")


def load_spec(spec_source: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Load a DOE spec. `spec_source` may be:
      - a file path string to a YAML file
      - a dict already parsed from YAML
    Returns the dict under 'FACTORS' (or 'factors').
    """
    doc = _load_yaml(spec_source)
    spec = doc.get("FACTORS", doc.get("factors"))
    if not isinstance(spec, dict):
        raise ValueError("DOE spec must contain a top-level 'FACTORS' (or 'factors') mapping")
    return spec


def load_base_project(template_source: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Load the base project template. `template_source` may be:
      - a file path string to a YAML file
      - a dict already parsed from YAML.
    Expects top-level 'PROJECTS' list; returns the first project dict.
    """
    doc = _load_yaml(template_source)
    projects = doc.get("PROJECTS")
    if not projects or not isinstance(projects, list):
        raise ValueError("Template must contain a top-level 'PROJECTS' list")
    return projects[0]


def build_designs(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Given a spec mapping each factor to { code: str, levels: [ ... ] }, compute
    the Cartesian product of all factor levels. Return a list of dicts mapping
    factor-code -> level value.
    """
    codes = []
    level_lists = []
    for factor in spec.values():
        codes.append(factor["code"])
        level_lists.append(factor["levels"])
    return [dict(zip(codes, combo)) for combo in itertools.product(*level_lists)]


def render_patches(
    spec: Dict[str, Any],
    base_project: Dict[str, Any],
    design: Dict[str, Any],
    exp_id: str,
) -> List[Dict[str, Any]]:
    """
    Given one design point (mapping code->value) and experiment ID,
    produce the list of JSON-Patch operations to apply to the wrapped base project.
    """
    from jinja2 import Template

    ctx = {**design, "EXP_ID": exp_id, "BASE_NAME": base_project.get("NAME")}
    patches: List[Dict[str, Any]] = []

    for factor in spec.values():
        for pt in factor.get("patches", []):
            # Check 'when' condition if present
            if "when" in pt:
                cond_tpl = Template(str(pt["when"]))
                cond_rendered = cond_tpl.render(**ctx)
                try:
                    should_apply = bool(yaml.safe_load(cond_rendered))
                except Exception:
                    should_apply = False
                if not should_apply:
                    continue

            raw_val = pt["value"]
            # If single-key dict with dot notation, fetch from ctx
            if isinstance(raw_val, dict) and len(raw_val) == 1:
                key = next(iter(raw_val))
                if "." in key:
                    val = _get_from_context(key, ctx)
                    patches.append({"op": pt["op"], "path": pt["path"], "value": val})
                    continue

            # Otherwise render via Jinja then parse YAML
            rendered = Template(str(raw_val)).render(**ctx)
            val = yaml.safe_load(rendered)
            patches.append({"op": pt["op"], "path": pt["path"], "value": val})

    return patches


def generate_payloads(
    spec_source: Union[str, Dict[str, Any]],
    template_source: Union[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Orchestrate DOE payload generation:
      1. Load spec dict (from file or inline)
      2. Load base project dict (from file or inline)
      3. Compute designs = Cartesian product of factor levels
      4. For each design:
         a. Render patches
         b. Wrap base_project under {PROJECTS: [ ... ]}
         c. Apply JSON-Patch
         d. Extract the first PROJECT and add 'EXPERIMENT' metadata
      5. Return the list of modified project dicts
    """
    spec = load_spec(spec_source)
    base_project = load_base_project(template_source)
    designs = build_designs(spec)
    payloads: List[Dict[str, Any]] = []

    for idx, design in enumerate(designs, start=1):
        exp_id = f"{idx:03d}"
        patches = render_patches(spec, base_project, design, exp_id)

        wrapper = {"PROJECTS": [deepcopy(base_project)]}
        result = jsonpatch.apply_patch(wrapper, patches, in_place=False)

        project = result["PROJECTS"][0]
        project["EXPERIMENT"] = {"FACTORS": design}
        payloads.append(project)

    return payloads


def write_payloads(
    payloads: List[Dict[str, Any]],
    output_path: Union[str, Path],
    force: bool = False,
) -> None:
    """
    Write out a YAML file with top-level 'PROJECTS': [ ... payloads ... ].
    If the file exists and force=False, raises FileExistsError.
    """
    out_data = {"PROJECTS": payloads}
    out_path = Path(output_path)
    if out_path.exists() and not force:
        raise FileExistsError(f"File '{output_path}' exists. Use force=True to overwrite.")
    out_path.write_text(yaml.safe_dump(out_data, sort_keys=False), encoding="utf-8")
