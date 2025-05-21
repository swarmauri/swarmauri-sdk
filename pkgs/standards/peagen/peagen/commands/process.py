# peagen/commands/process.py
"""Render or generate files for one or more projects."""

from __future__ import annotations

from peagen.slug_utils import slugify
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import typer

from peagen._api_key import _resolve_api_key
from peagen._config import _config
from peagen._source_packages import materialise_packages
from peagen.cli_common import (
    PathOrURI,
    common_peagen_options,
    load_peagen_toml,
    temp_workspace,
)
from peagen.core import Fore, Peagen
from peagen.plugin_registry import registry  # central plugin registry

process_app = typer.Typer(
    help="Render / generate one or all projects in a YAML payload."
)


@process_app.command("process")
@common_peagen_options
def process_cmd(
    ctx: typer.Context,
    projects_payload: str = typer.Argument(
        ..., help="YAML path/URI with a PROJECTS list."
    ),
    project_name: Optional[str] = typer.Option(
        None, help="Name of a single project to process."
    ),
    template_base_dir: Optional[str] = typer.Option(
        None, help="Root dir for template lookup."
    ),
    additional_package_dirs: Optional[str] = typer.Option(
        None, help="Comma-separated extra Jinja dirs."
    ),
    provider: Optional[str] = typer.Option(None, help="LLM provider ID."),
    model_name: Optional[str] = typer.Option(None, help="Model name to use."),
    trunc: bool = typer.Option(True, help="Truncate LLM responses."),
    start_idx: Optional[int] = typer.Option(None, help="Start at file index."),
    start_file: Optional[str] = typer.Option(None, help="Start at specific filename."),
    include_swarmauri: bool = typer.Option(
        True, "--include-swarmauri/--no-include-swarmauri"
    ),
    swarmauri_dev: bool = typer.Option(False, "--swarmauri-dev/--no-swarmauri-dev"),
    api_key: Optional[str] = typer.Option(None, help="Explicit LLM API key."),
    env: str = typer.Option(".env", help="Env-file path for LLM API key lookup."),
    verbose: int = typer.Option(0, "-v", "--verbose", count=True, help="Verbosity."),
    transitive: bool = typer.Option(
        False, "--transitive/--no-transitive", help="Only process transitive deps."
    ),
    workers: int = typer.Option(
        None, "--workers", "-w", help="Render worker pool size."
    ),
    agent_prompt_template_file: Optional[str] = typer.Option(
        None, help="Override system-prompt Jinja template."
    ),
    notify: Optional[str] = typer.Option(
        None, "--notify", help="Publisher URL or bare channel name."
    ),
    artifacts: Optional[str] = typer.Option(
        None, "--artifacts", "-a", help="dir://PATH or s3://ENDPOINT"
    ),
    org: Optional[str] = typer.Option(None, "--org", "-o", help="Organization slug."),
    access_key: Optional[str] = typer.Option(
        None, "--access-key", help="S3/MinIO access key."
    ),
    secret_key: Optional[str] = typer.Option(
        None, "--secret-key", help="S3/MinIO secret key."
    ),
    insecure: bool = typer.Option(
        False, "--insecure", help="When using s3://, disable TLS."
    ),
    plugin_mode: Optional[str] = typer.Option(
        None, "--plugin-mode", help="Plugin mode to use."
    ),
):
    """
    File: **process.py**
    Class: —
    Method: **process_cmd**

    Main *process* entry – now emits artefacts under
    projects/<project>/runs/<run-id>/, honours publishers.adapters layout.
    """
    toml_cfg = load_peagen_toml()
    plugins_cfg = toml_cfg.get("plugins", {})
    plugin_mode = plugin_mode if plugin_mode is not None else plugins_cfg.get("mode")
    ctx.obj.plugin_mode = plugin_mode
    _config["plugin_mode"] = plugin_mode

    # ── GENERAL & LLM ────────────────────────────────────────────────────
    workspace_cfg = toml_cfg.get("workspace", {})
    org = org if org is not None else workspace_cfg.get("org")
    workers = workers if workers is not None else workspace_cfg.get("workers", 0)

    llm_cfg = toml_cfg.get("llm", {})
    provider = provider if provider is not None else llm_cfg.get("default_provider")
    model_name = (
        model_name if model_name is not None else llm_cfg.get("default_model_name")
    )

    if api_key is None and provider:
        prov_tbl = llm_cfg.get(provider, {}) or llm_cfg.get(provider.lower(), {})
        api_key = prov_tbl.get("api_key") or prov_tbl.get("API_KEY")

    # ── STORAGE CONFIG (global) ──────────────────────────────────────────
    storage_cfg = toml_cfg.get("storage", {})
    adapters_cfg = storage_cfg.get("adapters", {})

    # derive artefacts URI (CLI override ➜ TOML default)
    if artifacts is None:
        default_store = storage_cfg.get("default_storage_adapter", "file")
        default_cfg = adapters_cfg.get(default_store, {})
        artifacts = (
            default_cfg.get("output_dir")
            if default_store == "file"
            else f"{default_store}://{default_cfg.get('endpoint')}"
        )

    # ── PUBLISHER CONFIG (supports publishers.adapters) ─────────────────
    pubs_cfg = toml_cfg.get("publishers", {})
    pub_adapters_cfg = pubs_cfg.get("adapters", {})
    default_publisher = pubs_cfg.get("default_publisher")

    if default_publisher and notify is None:
        notify = default_publisher

    # ── SANITY CHECKS ───────────────────────────────────────────────────
    if (start_idx and start_file) or (not provider or not model_name):
        typer.echo("❌ Invalid combination of flags.")
        raise typer.Exit(1)

    # ── BUILD PUBLISHER (optional) ──────────────────────────────────────
    bus = None
    channel = "peagen.events"
    if notify:
        nt = urlparse(notify)
        pub_name = nt.scheme or notify
        pub_cfg = pub_adapters_cfg.get(pub_name, {})
        # Allow overriding channel via notify URI path, e.g. redis://mychannel
        if nt.scheme and nt.path and nt.path != "/":
            channel = nt.path.lstrip("/")
        else:
            channel = pub_cfg.get("channel", channel)
        try:
            PubCls = registry["publishers"][pub_name]
        except KeyError:
            typer.echo(f"❌ Unknown publisher '{pub_name}'.")
            raise typer.Exit(1)
        bus = PubCls(**pub_cfg)
        bus.publish(channel, {"type": "process.started"})

    # ─────────────────────────────────────────────────────────────────────
    #  NEW: run-ID & project-prefix for one-bucket-per-org strategy
    # ─────────────────────────────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{timestamp}-{secrets.token_hex(4)}"
    typer.echo(f"run-id: {run_id}")

    project_slug = slugify(project_name or "multi")
    proj_prefix = f"projects/{project_slug}/runs/{run_id}/"  # ← canonical

    # ── BUILD STORAGE ADAPTER (prefix-aware) ────────────────────────────
    art = urlparse(artifacts or "")
    adapter_name = art.scheme or storage_cfg.get("default_storage_adapter", "file")

    try:
        StoreCls = registry["storage_adapters"][adapter_name]
    except KeyError:
        typer.echo(f"❌ Unknown storage adapter '{adapter_name}'.")
        raise typer.Exit(1)

    extra_store = dict(adapters_cfg.get(adapter_name, {}) or {})
    extra_store.setdefault("bucket", org)
    extra_store.setdefault("prefix", proj_prefix)
    storage_adapter = StoreCls(**extra_store)

    # ── PREPARE ENV & INSTANTIATE Peagen ────────────────────────────────
    projects_payload = PathOrURI(projects_payload)
    template_base_dir = PathOrURI(template_base_dir) if template_base_dir else None

    extra_dirs: List[Path] = []
    if additional_package_dirs:
        extra_dirs.extend(
            Path(p).expanduser() for p in additional_package_dirs.split(",")
        )

    source_pkgs = toml_cfg.get("source_packages", {}).get("package", [])

    if include_swarmauri:
        source_pkgs.append(
            {
                "type": "git",
                "uri": "https://github.com/swarmauri/swarmauri-sdk.git",
                "ref": "mono/dev" if swarmauri_dev else "master",
                "dest": "swarmauri_sdk",
            }
        )

    _config.update(truncate=trunc, revise=False, transitive=transitive, workers=workers)
    resolved_key = _resolve_api_key(provider, api_key, env)
    agent_env = {
        "provider": provider,
        "model_name": model_name,
        "api_key": resolved_key,
    }
    if agent_prompt_template_file:
        agent_env["agent_prompt_template_file"] = agent_prompt_template_file

    with temp_workspace() as ws:
        fetched_dirs = materialise_packages(source_pkgs, ws, storage_adapter)
        extra_dirs.extend(fetched_dirs)

        pea = Peagen(
            projects_payload_path=str(projects_payload),
            template_base_dir=str(template_base_dir) if template_base_dir else None,
            additional_package_dirs=extra_dirs,
            source_packages=source_pkgs,
            agent_env=agent_env,
            storage_adapter=storage_adapter,
            org=org,
            workspace_root=ws,
        )

        # ── LOG LEVEL ───────────────────────────────────────────────────
        if verbose >= 3:
            pea.logger.set_level(10)  # DEBUG
        elif verbose == 2:
            pea.logger.set_level(20)  # INFO
        elif verbose == 1:
            pea.logger.set_level(30)  # NOTICE

        # ── DISPATCH ────────────────────────────────────────────────────
        start = time.time()
        try:
            if project_name:
                _process_single(
                    pea, project_name, start_idx, start_file, transitive_only=transitive
                )
            else:
                pea.process_all_projects()
        except KeyboardInterrupt:
            typer.echo("\nInterrupted.  Bye.")
            raise typer.Exit(1)

        dur = time.time() - start
        pea.logger.info(f"{Fore.GREEN}Done in {dur:.1f}s{Fore.RESET}")

        if bus:
            bus.publish(channel, {"type": "process.done", "seconds": dur})


# ─────────────────────────────────────────────────────────────────────────────
#  Helper for single-project dispatch
# ─────────────────────────────────────────────────────────────────────────────
def _process_single(
    pea: Peagen,
    name: str,
    start_idx: Optional[int],
    start_file: Optional[str],
    *,
    transitive_only: bool,
) -> None:
    """
    File: **process.py**
    Class: —
    Method: **_process_single**

    Internal helper to keep `process_cmd` readable.
    """
    projects = pea.load_projects()
    project = next((p for p in projects if p.get("NAME") == name), None)
    if not project:
        pea.logger.error(f"Project '{name}' not found in payload.")
        raise typer.Exit(1)

    if start_file:
        pea.process_single_project(project, start_file=start_file)
    else:
        pea.process_single_project(
            project,
            start_idx=start_idx or 0,
            transitive_only=transitive_only,
        )
