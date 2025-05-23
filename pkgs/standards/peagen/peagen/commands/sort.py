# peagen/commands/sort.py
"""
Peagen “sort” sub-command – split out from cli.py.

Usage (wired in peagen/cli.py):
    from peagen.commands.sort import sort_app
    app.add_typer(sort_app, name="sort")
"""

import typer
from pprint import pformat
from pydantic import FilePath
from typing import Optional

from peagen.cli_common import load_peagen_toml

# ── absolute-import everything ────────────────────────────────────────────────
from peagen.core import Peagen, Fore, Style
from peagen._config import _config
from peagen._api_key import _resolve_api_key
from peagen._graph import get_immediate_dependencies

# ── Typer sub-app boilerplate ─────────────────────────────────────────────────
sort_app = typer.Typer(
    help="Sort and show the list of files that would be processed for a project (dry run)."
)


@sort_app.command("sort")
def sort(
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
        None, help="The LLM Provider (DeepInfra, LlamaCpp, Openai)"
    ),
    model_name: str = typer.Option(None, help="The model_name to use."),
    start_idx: int = typer.Option(
        None, help="Start at a certain file idx-wise (Use 'sort' to find idx number)"
    ),
    start_file: str = typer.Option(
        None, help="Start at a certain file name-wise (Use 'sort' to find filename)"
    ),
    include_swarmauri: bool = typer.Option(
        True,
        "--include-swarmauri/--no-swarmauri",
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
    transitive: bool = typer.Option(
        False,
        "--transitive/--no-transitive",
        help="If set, will only show transitive dependencies if start-file or start-idx is provided.",
    ),
    show_dependencies: bool = typer.Option(
        False,
        "--show-deps/--no-show-deps",
        help="If set, will show the direct dependenices of each file in the sort (one hop).",
    ),
    plugin_mode: Optional[str] = typer.Option(
        None, "--plugin-mode", help="Plugin mode to use."
    ),
):
    """
    Sort and show the list of files that would be processed for a project (Dry run).
    """
    if start_idx and start_file:
        typer.echo("[ERROR] Cannot assign both --start-idx and --start-file.")
        raise typer.Exit(code=1)

    if not project_name and (start_idx or start_file):
        typer.echo(
            "[ERROR] Cannot assign --start-idx or --start-file without --project-name."
        )
        raise typer.Exit(code=1)

    _config["transitive"] = transitive
    toml_cfg = load_peagen_toml()
    plugin_mode = (
        plugin_mode
        if plugin_mode is not None
        else toml_cfg.get("plugins", {}).get("mode")
    )
    _config["plugin_mode"] = plugin_mode

    # Convert additional_package_dirs from comma-delimited string to list[FilePath]
    additional_dirs_list = (
        additional_package_dirs.split(",") if additional_package_dirs else []
    )
    additional_dirs_list = [FilePath(_d) for _d in additional_dirs_list]

    resolved_key = _resolve_api_key(provider, api_key, env)

    pea = Peagen(
        projects_payload_path=str(projects_payload),
        template_base_dir=str(template_base_dir) if template_base_dir else None,
        additional_package_dirs=additional_dirs_list,
        agent_env={
            "provider": provider,
            "model_name": model_name,
            "api_key": resolved_key,
        },
        dry_run=True,
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
            pea.logger.error(f"Project '{project_name}' not found.")
            raise typer.Exit(code=1)

        if start_file:
            sorted_records, start_idx = pea.process_single_project(
                project, start_file=start_file
            )
        else:
            sorted_records, start_idx = pea.process_single_project(
                project, start_idx=start_idx or 0
            )

        pea.logger.info("")
        pea.logger.info(Fore.GREEN + f"\t[{project_name}]" + Style.RESET_ALL)
        for i, record in enumerate(sorted_records):
            idx = i + (start_idx or 0)
            name = record.get("RENDERED_FILE_NAME")
            deps = record.get("EXTRAS", {}).get("DEPENDENCIES", [])
            dep_str = ", ".join(deps) if deps else "None"
            pea.logger.info("")
            pea.logger.info(f"\t{idx}) {name}")
            if show_dependencies:
                deps = get_immediate_dependencies(sorted_records, name)
                pea.logger.info(f"\t\tDependencies: {dep_str}")

    else:
        projects_sorted_records = pea.process_all_projects()
        pea.logger.debug(pformat(projects_sorted_records))
        for sorted_records in projects_sorted_records:
            if not sorted_records:
                continue
            current_project_name = sorted_records[0].get(
                "PROJECT_NAME", "UnknownProject"
            )
            pea.logger.info("")
            pea.logger.info(
                Fore.GREEN + f"\t[{current_project_name}]" + Style.RESET_ALL
            )

            for i, record in enumerate(sorted_records):
                idx = i + (start_idx or 0)
                name = record.get("RENDERED_FILE_NAME")
                deps = record.get("EXTRAS", {}).get("DEPENDENCIES", [])
                dep_str = ", ".join(deps) if deps else "None"
                if show_dependencies:
                    pea.logger.info("")
                    pea.logger.info(f"\t{idx}) {name}")
                    deps = get_immediate_dependencies(sorted_records, name)
                    pea.logger.info(f"\t\tDependencies: {dep_str}")
                else:
                    pea.logger.info(f"\t{idx}) {name}")
