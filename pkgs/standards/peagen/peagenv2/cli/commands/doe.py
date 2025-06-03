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
from peagen.core.doe_core import DOECore
# We still import doe_handler so that “submit” can use it:
from peagen.handlers.doe_handler import doe_handler


doe_app = typer.Typer(help="Generate or submit DOE payload bundles.")


@doe_app.command("run")
def doe_run(
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
        False, "--skip-validate", help="Skip DOE spec validation"
    ),
):
    """
    Expand DOE *spec* × base *template* into a multi-project payload bundle, running locally.
    """
    logger = Logger(name="doe_run").logger
    logger.debug("Entering doe_run (local)")

    # 1) Load & validate spec if requested
    if not skip_validate:
        from peagen.commands.validate import _validate
        from peagen.schemas import DOE_SPEC_V1_1_SCHEMA

        spec_obj = yaml.safe_load(spec.read_text(encoding="utf-8"))
        try:
            _validate(spec_obj, DOE_SPEC_V1_1_SCHEMA, "DOE spec")
        except Exception as e:
            typer.echo(f"[ERROR] DOE spec validation failed: {e}")
            raise typer.Exit(1)

    # 2) Instantiate core and generate payloads
    try:
        core = DOECore(str(spec), str(template))
        payloads = core.generate_payloads()
    except Exception as e:
        typer.echo(f"[ERROR] {e}")
        raise typer.Exit(1)

    # 3) If dry_run: just show how many design points, then exit
    if dry_run:
        count = len(payloads)
        typer.echo(f"Dry-run: would expand {count} design points.")
        logger.info("Exiting doe_run (dry-run).")
        raise typer.Exit()

    # 4) Write the output bundle YAML
    try:
        core.write_payloads(str(output), force=force)
    except FileExistsError as fe:
        typer.echo(f"[ERROR] {fe}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"[ERROR] {e}")
        raise typer.Exit(1)

    typer.echo(f"✅  Wrote {output} ({len(payloads)} projects).")
    logger.debug("Exiting doe_run (local).")

    # 5) Optionally publish
    if notify:
        # Load .peagen.toml so the handler can look up publishers
        toml_cfg = load_peagen_toml(Path(config) if config else Path.cwd())
        pubs_cfg = toml_cfg.get("publishers", {})
        default_pub = pubs_cfg.get("default_publisher")
        notify_uri = notify or default_pub
        if not notify_uri:
            typer.echo("[WARN] No publisher configured; skipping notify.")
            return

        # Delegate to the same _publish_event logic as doe_handler
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

    # 1) Build args dict exactly as doe_handler expects
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

    # 2) Create a Pydantic Task instance
    task_id = str(uuid.uuid4())
    task = Task(id=task_id, pool="default", payload={"action": "doe", "args": args})

    # 3) Wrap in Work.start envelope
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

    # 4) POST to gateway
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
