# peagen/commands/process.py  · v2-compatible, legacy-flag safe, S3 artifacts support
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

import typer
import yaml

from peagen.cli_common import PathOrURI, common_peagen_options, load_peagen_toml
from peagen.core import Peagen, Fore
from peagen._config import _config
from peagen._api_key import _resolve_api_key
from peagen._gitops import _clone_swarmauri_repo

from peagen.publishers.redis_publisher import RedisPublisher  # IPublish impl
from peagen.storage_adapters.file_storage_adapter import FileStorageAdapter
from peagen.storage_adapters.minio_storage_adapter import MinioStorageAdapter

process_app = typer.Typer(help="Render / generate one or all projects in a YAML payload.")


@process_app.command("process")
@common_peagen_options
def process_cmd(
    ctx: typer.Context,

    # ── legacy positional ────────────────────────────────────────────────────
    projects_payload: str = typer.Argument(
        ...,
        help="YAML path/URI with a PROJECTS list (file:// default).",
    ),

    # ── legacy options (must stay) ───────────────────────────────────────────
    project_name: Optional[str] = typer.Option(None, help="Name of a single project to process."),
    template_base_dir: Optional[str] = typer.Option(
        None, help="Root directory for template lookup (file:// auto-prefix)."
    ),
    additional_package_dirs: Optional[str] = typer.Option(
        None,
        help="Comma-separated list of extra directories for Jinja loading.",
    ),
    provider: Optional[str] = typer.Option(None, help="LLM provider ID."),
    model_name: Optional[str] = typer.Option(None, help="Model name to use."),
    trunc: bool = typer.Option(True, help="Truncate LLM responses."),
    start_idx: Optional[int] = typer.Option(
        None, help="Start at file index (see `peagen sort`)."
    ),
    start_file: Optional[str] = typer.Option(
        None, help="Start at specific filename (see `peagen sort`)."
    ),
    include_swarmauri: bool = typer.Option(
        True, "--include-swarmauri/--no-include-swarmauri",
        help="Clone swarmauri-sdk into Jinja search path.",
    ),
    swarmauri_dev: bool = typer.Option(
        False, "--swarmauri-dev/--no-swarmauri-dev",
        help="Clone dev branch of swarmauri-sdk instead of main.",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        help="Explicit LLM API key; else we read <PROVIDER>_API_KEY env or .env.",
    ),
    env: str = typer.Option(".env", help="Env-file path for LLM API key lookup."),
    verbose: int = typer.Option(
        0, "-v", "--verbose", count=True, help="Verbosity (-v/-vv/-vvv)."
    ),

    # ── v2 additions ─────────────────────────────────────────────────────────
    transitive: bool = typer.Option(
        False, "--transitive/--no-transitive",
        help="Only process transitive dependencies when starting mid-stream.",
    ),
    workers: int = typer.Option(
        None, "--workers", "-w",
        help="Render worker pool size (0 = sequential).",
    ),
    agent_prompt_template_file: Optional[str] = typer.Option(
        None, help="Override system-prompt Jinja template."
    ),
    notify: Optional[str] = typer.Option(
        None, "--notify",
        help="Redis URL or bare channel name for event publishing.",
    ),

    # ── artifact storage flags ────────────────────────────────────────────────
    artifacts: Optional[str] = typer.Option(
        None, "--artifacts", "-a",
        help="Where to write outputs: dir://PATH or s3://ENDPOINT[/PREFIX]."
    ),
    org: Optional[str] = typer.Option(
        None, "--org", "-o",
        help="Organization slug (used as S3 bucket name and metadata)."
    ),
    access_key: Optional[str] = typer.Option(
        None, "--access-key",
        help="S3/MinIO access key (overrides AWS_ACCESS_KEY_ID)."
    ),
    secret_key: Optional[str] = typer.Option(
        None, "--secret-key",
        help="S3/MinIO secret key (overrides AWS_SECRET_ACCESS_KEY)."
    ),
    insecure: bool = typer.Option(
       False, "--insecure",
       help="When using s3://, disable TLS (use plain HTTP)."
    ),
):
    """
    Main *process* entry—keeps every legacy flag but speaks v2 under the hood.
    """
    # ── Merge in .peagen.toml values ───────────────────────────────────────
    toml_cfg = load_peagen_toml()

    # 1) GENERAL
    general = toml_cfg.get("general", {})
    org     = org     if org     is not None else general.get("org")
    workers = workers if workers is not None else general.get("workers", 0)

    # 2) LLM
    llm = toml_cfg.get("llm", {})
    provider        = provider        if provider        is not None else llm.get("default_provider")
    model_name      = model_name      if model_name      is not None else llm.get("default_model_name")
    default_temp    = llm.get("default_temperature", 1.0)
    default_max_tok = llm.get("default_max_tokens", 4096)

    # pull provider-specific API key out of [llm.<provider>]
    if api_key is None:
        prov_tbl = llm.get(provider, {}) or llm.get(provider.lower(), {})
        api_key = prov_tbl.get("api_key") or prov_tbl.get("API_KEY")

    # 3) STORAGE
    storage = toml_cfg.get("storage", {})
    # pick which adapter to use
    default_store = storage.get("default_storage_adapter", "file")
    # if user passed --artifacts, we'll parse that later; otherwise pick from TOML
    store_adapter = default_store if artifacts is None else None

    adapters = storage.get("adapters", {})
    file_cfg  = adapters.get("file", {})
    minio_cfg = adapters.get("minio", {})

    if artifacts is None:
        if default_store == "file":
            # local output_dir
            artifacts = file_cfg.get("output_dir")
        elif default_store == "minio":
            ep     = minio_cfg.get("endpoint")
            bucket = minio_cfg.get("bucket")
            artifacts = f"s3://{ep}"

    # 4) PUBLISHER
    pubs         = toml_cfg.get("publishers", {})
    default_pub  = pubs.get("default_publisher", {})
    redis_cfg    = pubs.get(default_pub, {})

    if redis_cfg:
        notify = "peagen.events"


    # ── Sanity checks ───────────────────────────────────────────────────────
    if start_idx and start_file:
        typer.echo("❌  Cannot use both --start-idx and --start-file.")
        raise typer.Exit(1)
    if not project_name and (start_idx or start_file):
        typer.echo("❌  --start-idx/start-file need --project-name.")
        raise typer.Exit(1)
    if not provider or not model_name:
        typer.echo("❌  --provider and --model-name are required (via CLI or .peagen.toml).")
        raise typer.Exit(1)

    # …later, in your RedisPublisher wiring…
    if notify:
        if "://" in notify:
            uri     = notify
            channel = "peagen.events"
        else:
            # build from TOML defaults under [publishers.redis]
            host     = redis_cfg.get("host", "localhost")
            port     = redis_cfg.get("port", 6379)
            db       = redis_cfg.get("db", 0)
            pwd      = redis_cfg.get("password")
            auth     = f":{pwd}@" if pwd else ""
            uri      = f"redis://{auth}{host}:{port}/{db}"
            channel  = notify
        bus = RedisPublisher(uri)
        bus.publish(channel, {"type": "process.started"})

    # …and your storage‐adapter selection can then test:
    if artifacts.startswith("s3://"):
        # use MinioStorageAdapter with access_key, secret_key from CLI or TOML:
        ak = access_key or minio_cfg.get("access_key_id")
        sk = secret_key or minio_cfg.get("secret_access_key")
        storage_adapter = MinioStorageAdapter(
            endpoint=minio_cfg.get("endpoint"),
            access_key=ak,
            secret_key=sk,
            bucket=minio_cfg.get("bucket"),
            secure=not insecure,
        )
    else:
        storage_adapter = FileStorageAdapter(root_dir=Path(artifacts or file_cfg.get("output_dir", ".")))

    # Convert to PathOrURI
    projects_payload = PathOrURI(projects_payload)
    template_base_dir = PathOrURI(template_base_dir) if template_base_dir else None

    # Prepare extra Jinja dirs
    extra_dirs: List[Path] = []
    if additional_package_dirs:
        extra_dirs.extend(Path(p).expanduser() for p in additional_package_dirs.split(","))
    if include_swarmauri:
        extra_dirs.append(Path(_clone_swarmauri_repo(use_dev_branch=swarmauri_dev)))

    # Runtime flags
    _config.update(
        truncate=trunc,
        revise=False,
        transitive=transitive,
        workers=workers,
    )

    # Build agent_env
    resolved_key = _resolve_api_key(provider, api_key, env)
    agent_env = {"provider": provider, "model_name": model_name, "api_key": resolved_key}
    if agent_prompt_template_file:
        agent_env["agent_prompt_template_file"] = agent_prompt_template_file

    # Instantiate engine
    pea = Peagen(
        projects_payload_path=str(projects_payload),
        template_base_dir=str(template_base_dir) if template_base_dir else None,
        additional_package_dirs=extra_dirs,
        agent_env=agent_env,
        storage_adapter=storage_adapter,
        org=org,
    )

    # Logging level
    if verbose >= 3:
        pea.logger.set_level(10)  # DEBUG
    elif verbose == 2:
        pea.logger.set_level(20)  # INFO
    elif verbose == 1:
        pea.logger.set_level(30)  # NOTICE

    # Dispatch
    start = time.time()
    try:
        if project_name:
            _process_single(
                pea, project_name, start_idx, start_file,
                transitive_only=transitive,
            )
        else:
            pea.process_all_projects()
    except KeyboardInterrupt:
        typer.echo("\nInterrupted.  Bye.")
        raise typer.Exit(1)

    dur = time.time() - start
    pea.logger.info(f"{Fore.GREEN}Done in {dur:.1f}s{Fore.RESET}")

    # Publish 'done'
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
            transitive_only=transitive_only
        )
