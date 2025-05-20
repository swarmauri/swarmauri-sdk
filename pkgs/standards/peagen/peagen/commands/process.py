# peagen/commands/process.py
from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import typer
from peagen._api_key import _resolve_api_key
from peagen._config import _config
from peagen._gitops import _clone_swarmauri_repo
from peagen.cli_common import PathOrURI, common_peagen_options, load_peagen_toml
from peagen.core import Fore, Peagen
from peagen.plugin_registry import registry  # central plugin registry
from peagen.utils import temp_workspace

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
):
    """
    Main *process* entry—keeps every legacy flag but speaks v2 under the hood.
    """
    toml_cfg = load_peagen_toml()

    # ── GENERAL & LLM ────────────────────────────────────────────────────────
    workspace = toml_cfg.get("workspace", {})
    org = org if org is not None else workspace.get("org")
    workers = workers if workers is not None else workspace.get("workers", 0)
    llm = toml_cfg.get("llm", {})
    provider = provider if provider is not None else llm.get("default_provider")
    model_name = model_name if model_name is not None else llm.get("default_model_name")

    if api_key is None and provider:
        prov_tbl = llm.get(provider, {}) or llm.get(provider.lower(), {})
        api_key = prov_tbl.get("api_key") or prov_tbl.get("API_KEY")

    # ── STORAGE CONFIG ────────────────────────────────────────────────────────
    storage_cfg = toml_cfg.get("storage", {})
    adapters = storage_cfg.get("adapters", {})

    # derive artifacts URI: CLI override or TOML default
    if artifacts is None:
        default_store = storage_cfg.get("default_storage_adapter", "file")
        default_cfg = adapters.get(default_store, {})
        artifacts = (
            default_cfg.get("output_dir")
            if default_store == "file"
            else f"{default_store}://{default_cfg.get('endpoint')}"
        )

    # ── PUBLISHER CONFIG ──────────────────────────────────────────────────────
    pubs = toml_cfg.get("publishers", {})
    default_pub = pubs.get("default_publisher")
    if default_pub and notify is None:
        notify = default_pub

    # ── SANITY CHECKS ─────────────────────────────────────────────────────────
    if (start_idx and start_file) or (not provider or not model_name):
        typer.echo("❌ Invalid combination of flags.")
        raise typer.Exit(1)

    # ── BUILD PUBLISHER ──────────────────────────────────────────────────────
    bus = None
    if notify:
        parsed_nt = urlparse(notify)
        pub_name = parsed_nt.scheme or notify

        # collect adapter-specific settings
        pub_cfg = pubs.get(pub_name, {}) or {}

        try:
            PubCls = registry["publishers"][pub_name]
        except KeyError:
            typer.echo(f"❌ Unknown publisher '{pub_name}'.")
            raise typer.Exit(1)

        bus = PubCls(**pub_cfg)
        # emit a “started” event
        channel = pub_cfg.get("channel", "peagen.events")
        bus.publish(channel, {"type": "process.started"})

    # ── BUILD STORAGE ADAPTER ─────────────────────────────────────────────────
    parsed_art = urlparse(artifacts or "")
    adapter_name = parsed_art.scheme or storage_cfg.get(
        "default_storage_adapter", "file"
    )

    try:
        StoreCls = registry["storage_adapters"][adapter_name]
    except KeyError:
        typer.echo(f"❌ Unknown storage adapter '{adapter_name}'.")
        raise typer.Exit(1)

    extra_store = adapters.get(adapter_name, {}) or {}
    storage_adapter = StoreCls(**extra_store)

    # ── PREPARE ENV & INSTANTIATE Peagen ────────────────────────────────────
    projects_payload = PathOrURI(projects_payload)
    template_base_dir = PathOrURI(template_base_dir) if template_base_dir else None

    extra_dirs: List[Path] = []
    if additional_package_dirs:
        extra_dirs.extend(
            Path(p).expanduser() for p in additional_package_dirs.split(",")
        )
    if include_swarmauri:
        extra_dirs.append(Path(_clone_swarmauri_repo(use_dev_branch=swarmauri_dev)))

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
        pea = Peagen(
            projects_payload_path=str(projects_payload),
            template_base_dir=str(template_base_dir) if template_base_dir else None,
            additional_package_dirs=extra_dirs,
            agent_env=agent_env,
            storage_adapter=storage_adapter,
            org=org,
            workspace_root=ws,
        )

        # ── LOG LEVEL ───────────────────────────────────────────────────────────
        if verbose >= 3:
            pea.logger.set_level(10)  # DEBUG
        elif verbose == 2:
            pea.logger.set_level(20)  # INFO
        elif verbose == 1:
            pea.logger.set_level(30)  # NOTICE

        # ── DISPATCH ────────────────────────────────────────────────────────────
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


def _process_single(
    pea: Peagen,
    name: str,
    start_idx: Optional[int],
    start_file: Optional[str],
    *,
    transitive_only: bool,
) -> None:
    """Helper to keep main function readable."""
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
