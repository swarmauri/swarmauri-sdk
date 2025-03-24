#!/usr/bin/env python3
"""
CLI for the ProjectFileGenerator

Enhancement: --api-key support with environment variable fallback.
"""

import os
import typer
from pydantic import FilePath
from pathlib import Path
from .core import ProjectFileGenerator, Fore, Back, Style
from ._config import _config
from ._banner import _print_banner
from ._gitops import _clone_swarmauri_repo
from ._api_key import _resolve_api_key

app = typer.Typer(help="CLI tool for processing project files using ProjectFileGenerator.")

_print_banner()


@app.command("process")
def process(
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    cwd: str = typer.Option(None, help="Optional cwd to execute in"),
    template_base_dir: str = typer.Option(None, help="Optional base directory for templates."),
    additional_package_dirs: str = typer.Option(
        None, 
        help="Optional list of additional directories to include in J2 env. Delimited by ','"
    ),
    provider: str = typer.Option(None, help="The LLM Provider (DeepInfra, LlamaCpp, Openai, etc.)"),
    model_name: str = typer.Option(None, help="The model_name to use."),
    trunc: bool = typer.Option(True, help="Truncate response (True or False)"),
    start_idx: int = typer.Option(None, help="Start at a certain file (Use sort to find idx number)"),
    start_file: str = typer.Option(None, help="Start at a certain file name-wise (Use sort to find filename)"),
    include_swarmauri: bool = typer.Option(
        True, 
        "--include-swarmauri/--no-include-swarmauri", 
        help="Include swarmauri-sdk in the environment by default."
    ),
    swarmauri_dev: bool = typer.Option(
        False,
        "--swarmauri-dev/--no-swarmauri-dev",
        help="Use the mono/dev branch of swarmauri-sdk instead of master."
    ),
    api_key: str = typer.Option(
        None, 
        help="API key used to authenticate with the selected provider. "
             "If omitted, we look up <PROVIDER>_API_KEY in the environment."
    ),
    env: str = typer.Option(
        ".env", 
        help="Filepath for env file used to authenticate with the selected provider. "
             "If omitted, we only load the environment."
    ),
    verbose: int = typer.Option(0, "-v", "--verbose", count=True, help="Verbosity level (-v, -vv, -vvv)"),
):
    """
    Process a single project specified by its PROJECT_NAME in the YAML payload.
    """
    if start_idx and start_file:
        typer.echo("[ERROR] Cannot assign both --start-idx and --start-file.")
        raise typer.Exit(code=1)

    if not project_name and (start_idx or start_file):
        typer.echo("[ERROR] Cannot assign --start-idx or --start-file without --project-name.")
        raise typer.Exit(code=1)

    # Convert additional_package_dirs from comma-delimited string to list[FilePath]
    additional_dirs_list = additional_package_dirs.split(',') if additional_package_dirs else []
    additional_dirs_list = [FilePath(_d) for _d in additional_dirs_list]

    # Conditionally include swarmauri-sdk by cloning and adding the tmpdir to additional_package_dirs
    if include_swarmauri:
        cloned_dir = _clone_swarmauri_repo(use_dev_branch=swarmauri_dev)
        additional_dirs_list.append(FilePath(cloned_dir))

    # Update config to set truncation
    _config["truncate"] = trunc

    # Resolve the appropriate API key
    resolved_key = _resolve_api_key(provider, api_key, env)

    try:
        base_dir = str(cwd) or os.getcwd()
        pfg = ProjectFileGenerator(
            base_dir=base_dir,
            projects_payload_path=str(projects_payload),
            template_base_dir=str(template_base_dir) if template_base_dir else None,
            additional_package_dirs=additional_dirs_list,
            agent_env={
                "provider": provider, 
                "model_name": model_name,
                "api_key": resolved_key,
            },
        )
        # Set verbosity level based on count
        if verbose == 1:
            pfg.logger.set_level(30)  # INFO
        elif verbose == 2:
            pfg.logger.set_level(20)  # DEBUG
        elif verbose >= 3:
            pfg.logger.set_level(10)  # VERBOSE

        if project_name:
            projects = pfg.load_projects()
            project = next((proj for proj in projects if proj.get("PROJECT_NAME") == project_name), None)
            if project is None:
                pfg.logger.info(f"Project '{project_name}' not found.")
                raise typer.Exit(code=1)
            if start_file:
                sorted_records, start_idx = pfg.process_single_project(project, start_file=start_file)
            else:
                sorted_records, start_idx = pfg.process_single_project(project, start_idx=start_idx or 0)
            pfg.logger.info(f"Processed project '{project_name}' successfully.")
        else:
            pfg.process_all_projects()
            pfg.logger.info("Processed all projects successfully.")
    except KeyboardInterrupt:
        typer.echo("\n  Interrupted... exited.")
        raise typer.Exit(code=1)


@app.command("sort")
def sort(
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    template_base_dir: str = typer.Option(None, help="Optional base directory for templates."),
    additional_package_dirs: str = typer.Option(
        None, 
        help="Optional list of additional directories to include in J2 env. Delimited by ','"
    ),
    provider: str = typer.Option(None, help="The LLM Provider (DeepInfra, LlamaCpp, Openai)"),
    model_name: str = typer.Option(None, help="The model_name to use."),
    start_idx: int = typer.Option(None, help="Start at a certain file idx-wise (Use sort to find idx number)"),
    start_file: str = typer.Option(None, help="Start at a certain file name-wise (Use sort to find filename)"),
    include_swarmauri: bool = typer.Option(
        True, 
        "--include-swarmauri/--no-include-swarmauri", 
        help="Include swarmauri-sdk in the environment by default."
    ),
    swarmauri_dev: bool = typer.Option(
        False,
        "--swarmauri-dev/--no-swarmauri-dev",
        help="Use the mono/dev branch of swarmauri-sdk instead of master."
    ),
    api_key: str = typer.Option(
        None, 
        help="API key used to authenticate with the selected provider. "
             "If omitted, we look up <PROVIDER>_API_KEY in the environment."
    ),
    env: str = typer.Option(
        ".env", 
        help="Filepath for env file used to authenticate with the selected provider. "
             "If omitted, we only load the environment."
    ),
    verbose: int = typer.Option(0, "-v", "--verbose", count=True, help="Verbosity level (-v, -vv, -vvv)"),
):
    """
    Sort and show the list of files that would be processed for a project (Dry run).
    """
    if start_idx and start_file:
        typer.echo("[ERROR] Cannot assign both --start-idx and --start-file.")
        raise typer.Exit(code=1)

    if not project_name and (start_idx or start_file):
        typer.echo("[ERROR] Cannot assign --start-idx or --start-file without --project-name.")
        raise typer.Exit(code=1)

    # Convert additional_package_dirs from comma-delimited string to list[FilePath]
    additional_dirs_list = additional_package_dirs.split(',') if additional_package_dirs else []
    additional_dirs_list = [FilePath(_d) for _d in additional_dirs_list]

    # Conditionally include swarmauri-sdk
    if include_swarmauri:
        cloned_dir = _clone_swarmauri_repo(use_dev_branch=swarmauri_dev)
        additional_dirs_list.append(FilePath(cloned_dir))

    # Resolve the appropriate API key
    resolved_key = _resolve_api_key(provider, api_key, env)

    pfg = ProjectFileGenerator(
        projects_payload_path=str(projects_payload),
        template_base_dir=str(template_base_dir) if template_base_dir else None,
        additional_package_dirs=additional_dirs_list,
        agent_env={
            "provider": provider,
            "model_name": model_name,
            "api_key": resolved_key,
        },
        dry_run=True
    )
    
    # Set verbosity level based on count
    if verbose == 1:
        pfg.logger.set_level(30)  # INFO
    elif verbose == 2:
        pfg.logger.set_level(20)  # DEBUG
    elif verbose >= 3:
        pfg.logger.set_level(10)  # VERBOSE

    if project_name:
        projects = pfg.load_projects()
        project = next((proj for proj in projects if proj.get("PROJECT_NAME") == project_name), None)
        if project is None:
            pfg.logger.error(f"Project '{project_name}' not found.")
            raise typer.Exit(code=1)

        if start_file:
            sorted_records, start_idx = pfg.process_single_project(project, start_file=start_file)
        else:
            sorted_records, start_idx = pfg.process_single_project(project, start_idx=start_idx or 0)

        pfg.logger.info("")
        pfg.logger.info(Fore.GREEN + f"\t[{project_name}]" + Style.RESET_ALL)
        for i, record in enumerate(sorted_records):
            pfg.logger.info(f'\t{i + start_idx}) {record.get("RENDERED_FILE_NAME")}')
    else:
        projects_sorted_records = pfg.process_all_projects()
        for sorted_records in projects_sorted_records:
            current_project_name = sorted_records[0].get("PROJECT_NAME")
            pfg.logger.info("")
            pfg.logger.info(Fore.GREEN + f"\t[{current_project_name}]" + Style.RESET_ALL)
            for i, record in enumerate(sorted_records):
                pfg.logger.info(f'\t{i}) {record.get("RENDERED_FILE_NAME")}')


@app.command("templates")
def get_templates(
    verbose: int = typer.Option(0, "-v", "--verbose", count=True, help="Verbosity level (-v, -vv, -vvv)")
):
    import ptree_dag.templates
    from pathlib import Path

    def detect_folders(path):
        try:
            directory = Path(path)
            if not directory.exists() or not directory.is_dir():
                return "Invalid or non-existent directory!"
            return [folder.name for folder in directory.iterdir() if folder.is_dir()]
        except PermissionError:
            return "Permission denied!"

    typer.echo('\nTemplate Directories:')
    namespace_dirs = list(ptree_dag.templates.__path__)
    for _n in namespace_dirs:
        typer.echo(f"- {_n}")

    templates = []
    for each in [detect_folders(_n) for _n in namespace_dirs]:
        if isinstance(each, list):
            templates.extend(each)

    typer.echo('\nTemplate Directories:')
    for _t in templates:
        typer.echo(f"- {_t}")


if __name__ == "__main__":
    app()