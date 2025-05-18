# peagen/commands/process.py  · v2-compatible, legacy-flag safe, S3 artifacts support
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

import typer
import yaml

from peagen.cli_common import PathOrURI, common_peagen_options
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
        0, "--workers", "-w",
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
    # Sanity checks
    if start_idx and start_file:
        typer.echo("❌  Cannot use both --start-idx and --start-file.")
        raise typer.Exit(1)
    if not project_name and (start_idx or start_file):
        typer.echo("❌  --start-idx/start-file need --project-name.")
        raise typer.Exit(1)
    if not provider or not model_name:
        typer.echo("❌  --provider and --model-name are required.")
        raise typer.Exit(1)

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

    # Event publisher
    bus = None
    if notify:
        uri = notify if "://" in notify else f"redis://localhost:6379/0"
        channel = notify if "://" not in notify else "peagen.events"
        bus = RedisPublisher(uri)
        bus.publish(channel, {"type": "process.started"})

    # Storage adapter selection
    storage_adapter = None
    if artifacts is None:
        # local working directory
        storage_adapter = FileStorageAdapter(root_dir=".")
    elif artifacts.startswith("dir://"):
        local_path = artifacts[len("dir://") :]
        storage_adapter = FileStorageAdapter(root_dir=local_path)
    elif artifacts.startswith("s3://"):
        # s3://ENDPOINT[/PREFIX]
        parsed = urlparse(artifacts)
        endpoint = parsed.netloc
        prefix = parsed.path.lstrip("/")  # optional
        if not org:
            typer.echo("❌  --org is required when using s3:// artifacts.")
            raise typer.Exit(1)
        ak = access_key or os.getenv("AWS_ACCESS_KEY_ID", "")
        sk = secret_key or os.getenv("AWS_SECRET_ACCESS_KEY", "")
        storage_adapter = MinioStorageAdapter(
            endpoint=endpoint,
            access_key=ak,
            secret_key=sk,
            bucket=org,
            secure=not insecure,
        )
        if prefix:
            class _PrefixedAdapter:
                def __init__(self, base, prefix):
                    self._base = base
                    self._prefix = prefix.rstrip("/") + "/"
                def upload(self, key, data):
                    return self._base.upload(self._prefix + key, data)
                def download(self, key):
                    return self._base.download(self._prefix + key)
            storage_adapter = _PrefixedAdapter(storage_adapter, prefix)
    else:
        typer.echo("❌  --artifacts must start with dir:// or s3://")
        raise typer.Exit(1)

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
