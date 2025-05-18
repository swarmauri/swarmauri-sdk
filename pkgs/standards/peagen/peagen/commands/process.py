import typer
from pathlib import Path
from typing import Optional

# ✅  all absolute
from peagen.core import Peagen, Fore, Style
from peagen._config import _config
from peagen._api_key import _resolve_api_key
from peagen._banner import _print_banner
from peagen._gitops import _clone_swarmauri_repo

process_app = typer.Typer(help="Process a project payload with Peagen.")

@process_app.command("process")
def process(
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    template_base_dir: str = typer.Option(None, help="Optional base directory for templates."),
    additional_package_dirs: str = typer.Option(
        None,
        help="Optional list of additional directories to include in J2 env. Delimited by ','",
    ),
    provider: str = typer.Option(None, help="The LLM Provider (DeepInfra, LlamaCpp, Openai, etc.)"),
    model_name: str = typer.Option(None, help="The model_name to use."),
    trunc: bool = typer.Option(True, help="Truncate response (True or False)"),
    start_idx: int = typer.Option(None, help="Start at a certain file (Use 'sort' to find idx number)"),
    start_file: str = typer.Option(None, help="Start at a certain file name-wise (Use 'sort' to find filename)"),
    include_swarmauri: bool = typer.Option(
        True, "--include-swarmauri/--no-include-swarmauri",
        help="Include swarmauri-sdk in the environment by default.",
    ),
    swarmauri_dev: bool = typer.Option(
        False, "--swarmauri-dev/--no-swarmauri-dev",
        help="Use the mono/dev branch of swarmauri-sdk instead of master.",
    ),
    api_key: str = typer.Option(
        None,
        help="API key used to authenticate with the selected provider."
             " If omitted, we look up <PROVIDER>_API_KEY in the environment.",
    ),
    env: str = typer.Option(".env", help="Filepath for env file used to authenticate."),
    verbose: int = typer.Option(0, "-v", "--verbose", count=True, help="Verbosity level (-v, -vv, -vvv)"),
    # NEW FLAGS:
    transitive: bool = typer.Option(
        False, "--transitive/--no-transitive",
        help="If set, will only process transitive dependencies if start-file or start-idx is provided.",
    ),
    workers: int = typer.Option(
        0, "--workers", "-w",
        help="Number of parallel workers for rendering (default 0 = sequential).",
    ),
    agent_prompt_template_file: str = typer.Option(
        None, help="Path to a custom agent prompt template file to be used in the agent environment.",
    ),
):
    """
    Process a single project specified by its PROJECT_NAME in the YAML payload.

    If --agent-prompt-template-file is used, it is passed along to the agent_env.
    """
    # Start timing
    start_time = time.time()

    if start_idx and start_file:
        typer.echo("[ERROR] Cannot assign both --start-idx and --start-file.")
        raise typer.Exit(code=1)
    if not project_name and (start_idx or start_file):
        typer.echo("[ERROR] Cannot assign --start-idx or --start-file without --project-name.")
        raise typer.Exit(code=1)

    # Convert additional_package_dirs from comma-delimited string to list[FilePath]
    additional_dirs_list = additional_package_dirs.split(",") if additional_package_dirs else []
    additional_dirs_list = [FilePath(_d) for _d in additional_dirs_list]

    # Include swarmauri-sdk if requested
    if include_swarmauri:
        from ._gitops import _clone_swarmauri_repo
        cloned_dir = _clone_swarmauri_repo(use_dev_branch=swarmauri_dev)
        additional_dirs_list.append(FilePath(cloned_dir))

    # Update global config
    _config["truncate"] = trunc
    _config["revise"] = False
    _config["transitive"] = transitive
    _config["workers"] = workers  # wire the new flag into config

    # Resolve API key and build agent_env
    resolved_key = _resolve_api_key(provider, api_key, env)
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
        # Set logging level
        if verbose == 1:
            pea.logger.set_level(30)  # INFO
        elif verbose == 2:
            pea.logger.set_level(20)  # DEBUG
        elif verbose >= 3:
            pea.logger.set_level(10)  # VERBOSE

        # Dispatch processing
        if project_name:
            projects = pea.load_projects()
            project = next((p for p in projects if p.get("NAME") == project_name), None)
            if project is None:
                pea.logger.error(f"Project '{project_name}' not found.")
                raise typer.Exit(code=1)

            if start_file:
                pea.process_single_project(project, start_file=start_file)
            else:
                pea.process_single_project(project, start_idx=start_idx or 0)

            pea.logger.info(f"Processed project '{project_name}' successfully.")
            # Log total duration
            duration = time.time() - start_time
            pea.logger.info(f"Total execution time: {duration:.2f} seconds")

        else:
            pea.process_all_projects()
            pea.logger.info("Processed all projects successfully.")
            # Log total duration
            duration = time.time() - start_time
            pea.logger.info(f"Total execution time: {duration:.2f} seconds")

    except KeyboardInterrupt:
        typer.echo("\n  Interrupted... exited.")
        raise typer.Exit(code=1)