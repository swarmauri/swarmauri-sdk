#!/usr/bin/env python3
"""
CLI for the ProjectFileGenerator

This script provides commands to process projects from a YAML payload using the core functionality.
"""

import typer
import typing
import pkgutil
from pydantic import FilePath
from .core import ProjectFileGenerator
from ._config import _config

app = typer.Typer(help="CLI tool for processing project files using ProjectFileGenerator.")

@app.command("process")
def process(
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    template_base_dir: str = typer.Option(None, help="Optional base directory for templates."),
    additional_package_dirs: str = typer.Option(None, help="Optional list of additional directories to include in J2 env. Delimited by ','"),
    provider: str = typer.Option(None, help="The LLM Provider (DeepInfra, LlamaCpp, Openai)"),
    model_name: str = typer.Option(None, help="The model_name to use."),
    trunc: bool = typer.Option(False, help="Truncate response (True or False)")
):
    """
    Process a single project specified by its PROJECT_NAME in the YAML payload.
    """
    additional_package_dirs = additional_package_dirs.split(',') if additional_package_dirs else []
    additional_package_dirs = [FilePath(_d) for _d in additional_package_dirs]

    # Set Response in config
    _config["truncate"] = trunc

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
            typer.echo(f"Project '{project_name}' not found.", err=True)
            raise typer.Exit(code=1)
        pfg.process_single_project(project)
        typer.echo(f"Processed project '{project_name}' successfully.")
    else:
        pfg.process_all_projects()
        typer.echo("Processed all projects successfully.")


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