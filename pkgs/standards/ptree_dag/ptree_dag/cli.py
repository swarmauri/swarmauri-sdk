#!/usr/bin/env python3
"""
CLI for the ProjectFileGenerator

This script provides commands to process projects from a YAML payload using the core functionality.
"""

import typer
import typing
import pkgutil
from pydantic import FilePath
from .core import ProjectFileGenerator, Fore, Back, Style
from ._config import _config
from ._banner import _print_banner
app = typer.Typer(help="CLI tool for processing project files using ProjectFileGenerator.")


_print_banner()


@app.command("process")
def process(
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    template_base_dir: str = typer.Option(None, help="Optional base directory for templates."),
    additional_package_dirs: str = typer.Option(None, help="Optional list of additional directories to include in J2 env. Delimited by ','"),
    provider: str = typer.Option(None, help="The LLM Provider (DeepInfra, LlamaCpp, Openai)"),
    model_name: str = typer.Option(None, help="The model_name to use."),
    trunc: bool = typer.Option(True, help="Truncate response (True or False)"),
    start_idx: int = typer.Option(0, help="Start at a certain file (Use sort to find idx number)"),
    start_file: str = typer.Option(None, help="Start at a certain file name-wise (Use sort to find filename)")
):
    """
    Process a single project specified by its PROJECT_NAME in the YAML payload.
    """
    if start_idx and start_file:
        pfg.logger.error(f"Cannot assign both start_idx and start_file.")
        raise typer.Exit(code=1)


    additional_package_dirs = additional_package_dirs.split(',') if additional_package_dirs else []
    additional_package_dirs = [FilePath(_d) for _d in additional_package_dirs]

    # Set Response in config
    _config["truncate"] = trunc

    try:
        pfg = ProjectFileGenerator(
            projects_payload_path=str(projects_payload),
            template_base_dir=str(template_base_dir) if template_base_dir else None,
            additional_package_dirs=additional_package_dirs,
            agent_env={"provider": provider, "model_name": model_name}
        )
        if project_name:
            projects = pfg.load_projects()
            # Look for a project with the matching "PROJECT_NAME" key
            project = next((proj for proj in projects if proj.get("PROJECT_NAME") == project_name), None)
            if project is None:
                pfg.logger.info(f"Project '{project_name}' not found.", err=True)
                raise typer.Exit(code=1)
            if start_file:
                sorted_records, start_idx = pfg.process_single_project(project, start_file=start_file)
            else:
                sorted_records, start_idx = pfg.process_single_project(project, start_idx=start_idx if start_idx else 0)
            pfg.logger.info(f"Processed project '{project_name}' successfully.")
        else:
            pfg.process_all_projects()
            pfg.logger.info("Processed all projects successfully.")
    except KeyboardInterrupt:
        typer.echo("\n  Interrupted... exited.")
        typer.Exit(code=1)


@app.command("sort")
def process(
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    template_base_dir: str = typer.Option(None, help="Optional base directory for templates."),
    additional_package_dirs: str = typer.Option(None, help="Optional list of additional directories to include in J2 env. Delimited by ','"),
    provider: str = typer.Option(None, help="The LLM Provider (DeepInfra, LlamaCpp, Openai)"),
    model_name: str = typer.Option(None, help="The model_name to use."),
    start_idx: int = typer.Option(None, help="Start at a certain file idx-wise (Use sort to find idx number)"),
    start_file: str = typer.Option(None, help="Start at a certain file name-wise (Use sort to find filename)")
):
    """
    Process a single project specified by its PROJECT_NAME in the YAML payload.
    """

    if start_idx and start_file:
        pfg.logger.error(f"Cannot assign both start_idx and start_file.")
        raise typer.Exit(code=1)


    additional_package_dirs = additional_package_dirs.split(',') if additional_package_dirs else []
    additional_package_dirs = [FilePath(_d) for _d in additional_package_dirs]

    pfg = ProjectFileGenerator(
        projects_payload_path=str(projects_payload),
        template_base_dir=str(template_base_dir) if template_base_dir else None,
        additional_package_dirs=additional_package_dirs,
        agent_env={"provider": provider, "model_name": model_name},
        dry_run=True
    )
    if project_name:
        projects = pfg.load_projects()
        # Look for a project with the matching "PROJECT_NAME" key
        project = next((proj for proj in projects if proj.get("PROJECT_NAME") == project_name), None)
        if project is None:
            pfg.logger.error(f"Project '{project_name}' not found.")
            raise typer.Exit(code=1)

        if start_file:
            sorted_records, start_idx = pfg.process_single_project(project, start_file=start_file)
        else:
            sorted_records, start_idx = pfg.process_single_project(project, start_idx=start_idx if start_idx else 0)
        pfg.logger.info("")
        pfg.logger.info(Fore.GREEN + f"\t{[project_name]}" + Style.RESET_ALL)
        for _, record in enumerate(sorted_records):
            pfg.logger.info(f'\t{_+start_idx}) {record.get("RENDERED_FILE_NAME")}')
        
    else:
        projects_sorted_records = pfg.process_all_projects()
        for sorted_records in projects_sorted_records:
            project_name = sorted_records[0].get("PROJECT_NAME")
            pfg.logger.info("")
            pfg.logger.info(Fore.GREEN + f"\t{[project_name]}" + Style.RESET_ALL)
            for _, record in enumerate(sorted_records):
                pfg.logger.info(f'\t{_}) {record.get("RENDERED_FILE_NAME")}')
        

@app.command("templates")
def get_templates():
    import ptree_dag.templates
    from pathlib import Path

    def detect_folders(path):
        try:
            # Convert string path to Path object
            directory = Path(path)
            # Check if path exists and is a directory
            if not directory.exists() or not directory.is_dir():
                return "Invalid or non-existent directory!"
            # List only directories
            folders = [folder.name for folder in directory.iterdir() if folder.is_dir()]
            return folders
        except PermissionError:
            return "Permission denied!"

    typer.echo('\nTemplate Directories:')
    namespace_dirs = list(ptree_dag.templates.__path__)
    for _n in namespace_dirs:
        typer.echo(f"- {_n}")

    templates = []
    for each in [detect_folders(_n) for _n in namespace_dirs]:
        templates.extend(each)
    

    typer.echo('\nTemplate Directories:')
    for _t in templates:
        typer.echo(f"- {_t}")

if __name__ == "__main__":
    app()