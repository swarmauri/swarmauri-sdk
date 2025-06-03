# peagen/commands/doe.py

from __future__ import annotations

import typer
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from swarmauri_standard.loggers.Logger import Logger

from peagen.cli_common import load_peagen_toml
from peagen.models import Task
from peagen.handlers.doe_handler import doe_handler

# Core functions (restructured to be module-level)
from peagen.core.doe_core import (
    load_spec_and_template,
    build_designs,
    render_patches,
    apply_patches_to_base,
    generate_payloads,
    write_payloads,
)

doe_app = typer.Typer(help="Generate or submit DOE payload bundles.")


@doe_app.command("run")
def doe_run(
    spec: Path = typer.Argument(..., exists=True, help="Path to DOE spec (.yml)"),
    template: Path = typer.Argument(..., exists=True, help="Base project template (.yml)"),
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
        False, "--skip-validate", help="Skip DOE spec validation"
    ),
):
    """
    Expand DOE *spec* × base *template* into a multi-project payload bundle, running locally.
    """
    logger = Logger(name="doe_run").logger
    logger.debug("Entering doe_run (local)")

    # 1) Load DOE spec & template
    try:
        spec_dict, base_project = load_spec_and_template(str(spec), str(template))
    except Exception as e:
        typer.echo(f"[ERROR] Loading spec/template failed: {e}")
        raise typer.Exit(1)

    # 2) Optionally validate spec (skip_validate controls)
    if not skip_validate:
        from peagen.commands.validate import _validate
        from peagen.schemas import DOE_SPEC_V1_1_SCHEMA

        try:
            _validate(spec_dict, DOE_SPEC_V1_1_SCHEMA, "DOE spec")
        except Exception as e:
            typer.echo(f"[ERROR] DOE spec validation failed: {e}")
            raise typer.Exit(1)

    # 3) Build designs (cartesian product)
    try:
        designs = build_designs(spec_dict)
    except Exception as e:
        typer.echo(f"[ERROR] Building design matrix failed: {e}")
        raise typer.Exit(1)

    # 4) If dry_run: report count and exit
    if dry_run:
        count = len(designs)
        typer.echo(f"Dry-run: would expand {count} design points.")
        logger.info("Exiting doe_run (dry-run).")
        raise typer.Exit()

    # 5) Generate full payloads
    try:
        payloads = generate_payloads(spec_dict, base_project)
    except Exception as e:
        typer.echo(f"[ERROR] Generating payloads failed: {e}")
        raise typer.Exit(1)

    # 6) Write output bundle
    try:
        write_payloads(payloads, str(output), force=force)
    except FileExistsError as fe:
        typer.echo(f"[ERROR] {fe}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"[ERROR] Writing output failed: {e}")
        raise typer.Exit(1)

    typer.echo(f"✅  Wrote {output} ({len(payloads)} projects).")
    logger.debug("Exiting doe_run (local).")

    # 7) Optionally publish completion
    if notify:
        toml_cfg = load_peagen_toml(Path(config) if config else Path.cwd())
        pubs_cfg = toml_cfg.get("publishers", {})
        default_pub = pubs_cfg.get("default_publisher")
        notify_uri = notify or default_pub
        if not notify_uri:
            typer.echo("[WARN] No publisher configured; skipping notify.")
            return

        from peagen.handlers.doe_handler import _publish_event

        try:
            _publish_event(
                notify_uri, str(output), len(payloads), config or ".peagen.toml"
            )
        except Exception as e:
            typer.echo(f"[ERROR] Publish event failed: {e}")


@doe_app.command("submit")
def doe_submit(
    spec: Path = typer.Argument(..., exists=True, help="Path to DOE spec (.yml)"),
    template: Path = typer.Argument(..., exists=True, help="Base project template (.yml)"),
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
        False, "--skip-validate", help="Skip DOE spec validation"
    ),
    gateway_url: str = typer.Option(
        "http://localhost:8000/rpc", "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    """
    Submit DOE generation as a background task. Returns immediately with a taskId.
    """
    logger = Logger(name="doe_submit").logger
    logger.debug("Entering doe_submit (remote)")

    # Build args for handler
    args: Dict[str, Any] = {
        "spec": str(spec),
        "template": str(template),
        "output": str(output),
        "config": config,
        "notify": notify,
        "dry_run": dry_run,
        "force": force,
        "skip_validate": skip_validate,
    }

    # Create Task
    task_id = str(uuid.uuid4())
    task = Task(id=task_id, pool="default", payload={"action": "doe", "args": args})

    # Build Work.start envelope
    envelope = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "Work.start",
        "params": {
            "id": task.id,
            "pool": task.pool,
            "payload": task.payload,
        },
    }

    # POST to gateway
    try:
        import httpx

        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted DOE generation → taskId={task.id}")
    except Exception as exc:
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
