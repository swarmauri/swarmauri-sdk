# peagen/commands/revise.py
"""
Peagen “revise” sub-command – split out from cli.py.

Usage (wired in peagen/cli.py):
    app.add_typer(revise_app, name="revise")
"""

import json
from pathlib import Path
from pprint import pformat
from typing import Optional

import typer
from pydantic import FilePath
from peagen.cli_common import load_peagen_toml

# ── absolute-import everything ────────────────────────────────────────────────
from peagen._api_key import _resolve_api_key
from peagen._config import _config
from peagen.core import Peagen

# ── Typer sub-app boilerplate ─────────────────────────────────────────────────
revise_app = typer.Typer(help="Revise an existing Peagen project.")


# Note: we keep `@revise_app.callback()` so that “peagen revise …” works exactly
# like before; swap to @revise_app.command() if you prefer a nested sub-command.
@revise_app.command("revise")
def revise(
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    template_base_dir: str = typer.Option(
        None, help="Optional base directory for templates."
    ),
    additional_package_dirs: str = typer.Option(
        None,
        help="Optional list of additional directories to include in J2 env. Delimited by ','",
    ),
    provider: str = typer.Option(
        None, help="The LLM Provider (DeepInfra, LlamaCpp, Openai, etc.)"
    ),
    model_name: str = typer.Option(None, help="The model_name to use."),
    trunc: bool = typer.Option(True, help="Truncate response (True or False)"),
    start_idx: int = typer.Option(
        None, help="Start at a certain file (Use 'sort' to find idx number)"
    ),
    start_file: str = typer.Option(
        None, help="Start at a certain file name-wise (Use 'sort' to find filename)"
    ),
    include_swarmauri: bool = typer.Option(
        True,
        "--include-swarmauri/--no-include-swarmauri",
        help="Include swarmauri-sdk in the environment by default.",
    ),
    swarmauri_dev: bool = typer.Option(
        False,
        "--swarmauri-dev/--no-swarmauri-dev",
        help="Use the mono/dev branch of swarmauri-sdk instead of master.",
    ),
    api_key: str = typer.Option(
        None,
        help="API key used to authenticate with the selected provider. "
        "If omitted, we look up <PROVIDER>_API_KEY in the environment.",
    ),
    env: str = typer.Option(
        ".env",
        help="Filepath for env file used to authenticate with the selected provider. "
        "If omitted, we only load the environment.",
    ),
    verbose: int = typer.Option(
        0, "-v", "--verbose", count=True, help="Verbosity level (-v, -vv, -vvv)"
    ),
    revision_notes: Optional[str] = typer.Option(
        None,
        "--revision-notes",
        help="Inline text for revision notes (required if --revise is used without --revision-notes-file).",
    ),
    revision_notes_file: Optional[Path] = typer.Option(
        None,
        "--revision-notes-file",
        help="File containing revision notes (.yaml, .yml, .json, or raw text).",
    ),
    # NEW TRANSITIVE FLAG
    transitive: bool = typer.Option(
        False,
        "--transitive/--no-transitive",
        help="If set, will only process transitive dependencies if start-file or start-idx is provided.",
    ),
    # NEW AGENT PROMPT TEMPLATE FLAG
    agent_prompt_template_file: str = typer.Option(
        None,
        help="Path to a custom agent prompt template file to be used in the agent environment.",
    ),
    plugin_mode: Optional[str] = typer.Option(
        None, "--plugin-mode", help="Plugin mode to use."
    ),
):
    """
    Revise a single project specified by its PROJECT_NAME in the YAML payload.

    If --revise is used, either --revision-notes or --revision-notes-file is required.
    If --agent-prompt-template-file is used, it is passed along to the agent_env.
    """
    if start_idx and start_file:
        typer.echo("[ERROR] Cannot assign both --start-idx and --start-file.")
        raise typer.Exit(code=1)

    if not project_name and (start_idx or start_file):
        typer.echo(
            "[ERROR] Cannot assign --start-idx or --start-file without --project-name."
        )
        raise typer.Exit(code=1)

    # -------- NEW LOGIC FOR REVISION NOTES --------
    # Must provide at least one of --revision-notes or --revision-notes-file
    if not (revision_notes or revision_notes_file):
        typer.echo(
            "[ERROR] The --revise flag requires either "
            "--revision-notes or --revision-notes-file."
        )
        raise typer.Exit(code=1)

    notes_text = None
    if revision_notes_file is not None:
        try:
            suffix = revision_notes_file.suffix.lower()
            if suffix in [".yaml", ".yml"]:
                import yaml

                with open(revision_notes_file, "r") as f:
                    loaded_data = yaml.safe_load(f)
                notes_text = pformat(loaded_data)
            elif suffix == ".json":
                with open(revision_notes_file, "r") as f:
                    loaded_data = json.load(f)
                notes_text = pformat(loaded_data)
            else:
                # Fallback to reading plain text
                notes_text = revision_notes_file.read_text()
        except Exception as exc:
            typer.echo(f"[ERROR] Failed to read/parse revision notes file: {exc}")
            raise typer.Exit(code=1)
    else:
        notes_text = revision_notes
    _config["revision_notes"] = notes_text

    # Convert additional_package_dirs from comma-delimited string to list[FilePath]
    additional_dirs_list = (
        additional_package_dirs.split(",") if additional_package_dirs else []
    )
    additional_dirs_list = [FilePath(_d) for _d in additional_dirs_list]

    # Conditionally include swarmauri-sdk by cloning and adding the tmpdir to additional_package_dirs
    if include_swarmauri:
        from peagen._gitops import _clone_swarmauri_repo

        cloned_dir = _clone_swarmauri_repo(use_dev_branch=swarmauri_dev)
        additional_dirs_list.append(FilePath(cloned_dir))

    # Update config to set truncation, revision, and transitive
    _config["truncate"] = trunc
    _config["revise"] = True
    _config["transitive"] = transitive
    toml_cfg = load_peagen_toml()
    plugin_mode = (
        plugin_mode
        if plugin_mode is not None
        else toml_cfg.get("plugins", {}).get("mode")
    )
    _config["plugin_mode"] = plugin_mode

    # Resolve the appropriate API key
    resolved_key = _resolve_api_key(provider, api_key, env)

    # Build the agent_env
    agent_env = {
        "provider": provider,
        "model_name": model_name,
        "api_key": resolved_key,
    }
    if agent_prompt_template_file:
        agent_env["agent_prompt_template_file"] = agent_prompt_template_file

    try:
        pea = Peagen(
            projects_payload_path=str(projects_payload),
            template_base_dir=str(template_base_dir) if template_base_dir else None,
            additional_package_dirs=additional_dirs_list,
            agent_env=agent_env,
        )
        if verbose == 1:
            pea.logger.set_level(30)  # INFO
        elif verbose == 2:
            pea.logger.set_level(20)  # DEBUG
        elif verbose >= 3:
            pea.logger.set_level(10)  # VERBOSE

        if project_name:
            projects = pea.load_projects()
            pea.logger.debug(pformat(projects))
            project = next(
                (proj for proj in projects if proj.get("NAME") == project_name), None
            )
            if project is None:
                pea.logger.info(f"Project '{project_name}' not found.")
                raise typer.Exit(code=1)
            if start_file:
                sorted_records, start_idx = pea.process_single_project(
                    project, start_file=start_file
                )
            else:
                sorted_records, start_idx = pea.process_single_project(
                    project, start_idx=start_idx or 0
                )
            pea.logger.info(f"Processed project '{project_name}' successfully.")
        else:
            pea.process_all_projects()
            pea.logger.info("Processed all projects successfully.")
    except KeyboardInterrupt:
        typer.echo("\n  Interrupted... exited.")
        raise typer.Exit(code=1)
