# peagen/commands/doe.py
"""
peagen doe – expand a DOE spec + base template into a project-payloads bundle.

Wire in cli.py with:
    from peagen.commands.doe import doe_app
    app.add_typer(doe_app, name="doe")
"""

from __future__ import annotations

import hashlib
import itertools
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional

from peagen.commands.validate import _validate
from peagen.schemas import DOE_SPEC_V1_SCHEMA

import typer
import yaml
from urllib.parse import urlparse

from peagen.cli_common import load_peagen_toml
from peagen.plugin_registry import registry

doe_app = typer.Typer(help="Generate project-payloads.yaml from a DOE spec.")

# --------------------------------------------------------------------------- helpers
LLM_FALLBACK_KEYS = {
    "provider",
    "model",
    "temperature",
    "max_tokens",
    "max_context_tokens",
    "top_p",
    "frequency_penalty",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_yaml(uri: str | Path) -> Dict:
    p = Path(uri).expanduser()
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def _write_yaml(data: Dict, path: Path, force: bool) -> None:
    if path.exists() and not force:
        typer.echo(f"❌  File '{path}' exists. Use --force to overwrite.")
        raise typer.Exit(code=1)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _apply_json_patch(doc: Dict, patch_ops: List[Dict]) -> None:
    import jsonpatch

    jsonpatch.JsonPatch(patch_ops).apply(doc, in_place=True)


def _is_llm_key(key: str, spec_llm_keys: set[str]) -> bool:
    return key in spec_llm_keys or key in LLM_FALLBACK_KEYS


# ---------------------------------------------------------------- print matrix
def _print_design_matrix(
    llm_keys: List[str],
    other_keys: List[str],
    design_points: List[Dict],
) -> None:
    """Pretty table of every design point."""
    headers = ["ID"] + llm_keys + other_keys
    # column widths
    col_w = [max(len(h), 2) for h in headers]
    for idx, pt in enumerate(design_points):
        for c, k in enumerate(llm_keys + other_keys, start=1):
            col_w[c] = max(col_w[c], len(str(pt.get(k, ""))))

    def _row(cells):
        return "  ".join(str(v).ljust(col_w[i]) for i, v in enumerate(cells))

    typer.echo(_row(headers))
    typer.echo(_row(["-" * w for w in col_w]))

    for idx, pt in enumerate(design_points):
        cells = [f"{idx:03d}"] + [pt.get(k, "") for k in llm_keys + other_keys]
        typer.echo(_row(cells))


# --------------------------------------------------------------------------- CLI
@doe_app.command("gen")
def experiment_generate(
    spec: Path = typer.Argument(..., exists=True, help="Path to DOE spec (.yml)"),
    template: Path = typer.Argument(..., exists=True, help="Base project template"),
    output: Path = typer.Option(
        "project_payloads.yaml", "--output", "-o", help="Where to write bundle"
    ),
    config: Optional[str] = typer.Option(
        ".peagen.toml", "-c", "--config", help="Alternate .peagen.toml path."
    ),
    notify: Optional[str] = typer.Option(
        None, "--notify", help="Bus URI to publish completion event"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print matrix only"),
    force: bool = typer.Option(False, "--force", help="Overwrite output file"),
    skip_validate: bool = typer.Option(
        False,
        "--skip-validate",
        help="Skip DOE spec validation",
    ),
):
    """
    Expand DOE *spec* × base *template* into a multi-project payload bundle.
    """

    toml_cfg = load_peagen_toml(Path(config) if config else Path.cwd())
    pubs_cfg = toml_cfg.get("publishers", {})
    default_pub = pubs_cfg.get("default_publisher")

    if default_pub and notify is None:
        notify = default_pub

    if notify:
        nt = urlparse(notify)
        pub_name = nt.scheme or notify
        try:
            registry["publishers"][pub_name]
        except KeyError:
            typer.echo(f"❌ Unknown publisher '{pub_name}'.")
            raise typer.Exit(1)

    # 1. ---------- load files -------------------------------------------------
    spec_obj = _load_yaml(spec)
    template_obj = _load_yaml(template)

    # validate spec unless skipped
    if not skip_validate:
        _validate(spec_obj, DOE_SPEC_V1_SCHEMA, "DOE spec")

    llm_map = spec_obj.get("LLM_FACTORS", {})
    other_map = spec_obj.get("FACTORS", {})

    # fallback for old specs that have only FACTORS
    if not llm_map:
        guessed = {k: v for k, v in other_map.items() if _is_llm_key(k, set())}
        llm_map = guessed
        other_map = {k: v for k, v in other_map.items() if k not in guessed}

    # 2. ---------- build cartesian product -----------------------------------
    # we can replace once we've developed swarmauri.matrices.*
    def _matrix(factor_map: Dict[str, List]) -> List[List[tuple]]:
        """
        Convert a map of factors -> level-list into a cartesian product, accepting
        both legacy and rich factor formats.

        Rich format example:
            {"temperature": {"levels":[0.2,0.7], "code":"T"}, ...}
        Legacy format:
            {"temperature": [0.2,0.7], ...}
        """
        if not factor_map:
            return [()]

        lists = []
        for k, spec in factor_map.items():
            if isinstance(spec, dict) and "levels" in spec:
                level_values = spec["levels"]
            else:
                level_values = spec
            lists.append([(k, v) for v in level_values])

        return list(itertools.product(*lists))

    design_points: List[Dict] = [
        dict(llm + oth)
        for llm in _matrix(llm_map)
        for oth in _matrix(other_map or {"_dummy": [None]})
    ]

    # 3. ---------- generate projects -----------------------------------------
    projects = []
    spec_name = spec.stem
    peagen_ver = "0.0"  # lazy: importlib.metadata.version("peagen")
    for idx, point in enumerate(design_points):
        proj = deepcopy(template_obj)

        # apply factor-specific patches
        for patch_rule in spec_obj.get("PATCHES", []):
            when: Dict = patch_rule.get("when", {})
            if all(point.get(k) == v for k, v in when.items()):
                _apply_json_patch(proj, patch_rule["apply"])

        # META building
        llm_factors = {k: point[k] for k in llm_map}
        other_factors = {k: point[k] for k in other_map if k in point}

        meta = {
            "design_id": f"{spec_name}-{idx:03d}",
            "LLM_FACTORS": llm_factors,
            "factors": other_factors,
            "spec_name": spec_name,
            "peagen_version": peagen_ver,
        }
        proj.setdefault("META", {}).update(meta)

        projects.append(proj)

    bundle = {
        "PROJECTS": projects,
        "SOURCE": {
            "spec": str(spec),
            "template": str(template),
            "spec_checksum": _sha256(spec),
        },
    }

    # 4. ---------- output / dry-run / notify ----------------------------------
    typer.echo(f"Expanded {len(projects)} design points:")
    for p in projects:
        did = p["META"]["design_id"]
        llm_str = ", ".join(f"{k}={v}" for k, v in p["META"]["LLM_FACTORS"].items())
        other_str = ", ".join(f"{k}={v}" for k, v in p["META"]["factors"].items())
        typer.echo(f"  {did:<20} {llm_str}  {other_str}")

    if dry_run:
        typer.echo("")  # blank line before the table
        _print_design_matrix(
            list(llm_map.keys()),
            list(other_map.keys()),
            design_points,
        )
        typer.echo("\nDry-run complete – matrix printed above; no file written.")
        raise typer.Exit()

    _write_yaml(bundle, output, force)
    typer.echo(f"✅  Wrote {output} ({output.stat().st_size / 1024:.1f} KB)")

    if notify:
        _publish_event(notify, output, len(projects), config)


# --------------------------------------------------------------------- notifier
def _publish_event(uri: str, output: Path, count: int, config: Optional[str]) -> None:
    """Publish a ``peagen.experiment.done`` event using the configured publisher."""

    nt = urlparse(uri)
    pub_name = nt.scheme or uri

    toml_cfg = load_peagen_toml(Path(config) if config else Path.cwd())
    pubs_cfg = toml_cfg.get("publishers", {})
    adapters_cfg = pubs_cfg.get("adapters", {})

    channel = "peagen.events"
    pub_cfg = adapters_cfg.get(pub_name, {})
    if nt.scheme and nt.path and nt.path != "/":
        channel = nt.path.lstrip("/")
    else:
        channel = pub_cfg.get("channel", channel)

    try:
        PubCls = registry["publishers"][pub_name]
    except KeyError:
        typer.echo(f"❌ Unknown publisher '{pub_name}'.")
        return

    bus = PubCls(**pub_cfg)
    bus.publish(
        channel,
        {
            "type": "peagen.experiment.done",
            "output": str(output),
            "count": count,
        },
    )
