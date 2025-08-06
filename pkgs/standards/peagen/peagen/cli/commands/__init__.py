"""Expose all Typer sub-applications for the CLI."""

from peagen.cli.commands.doe import local_doe_app, remote_doe_app
from peagen.cli.commands.eval import local_eval_app, remote_eval_app
from peagen.cli.commands.extras import local_extras_app, remote_extras_app
from peagen.cli.commands.fetch import fetch_app
from peagen.cli.commands.db import local_db_app, remote_db_app
from peagen.cli.commands.init import local_init_app, remote_init_app
from peagen.cli.commands.process import local_process_app, remote_process_app
from peagen.cli.commands.mutate import local_mutate_app, remote_mutate_app
from peagen.cli.commands.evolve import local_evolve_app, remote_evolve_app
from peagen.cli.commands.sort import local_sort_app, remote_sort_app
from peagen.cli.commands.task import remote_task_app
from peagen.cli.commands.analysis import local_analysis_app, remote_analysis_app
from peagen.cli.commands.templates import (
    local_template_sets_app,
    remote_template_sets_app,
)
from peagen.cli.commands.tui import dashboard_app
from peagen.cli.commands.validate import local_validate_app, remote_validate_app
from peagen.cli.commands.publickey import (
    local_publickey_app,
    remote_publickey_app,
)
from peagen.cli.commands.deploykey import (
    local_deploykey_app,
    remote_deploykey_app,
)
from peagen.cli.commands.secrets import local_secrets_app, remote_secrets_app
from peagen.cli.commands.show import show_app

__all__ = [
    "local_doe_app",
    "remote_doe_app",
    "local_eval_app",
    "remote_eval_app",
    "local_mutate_app",
    "remote_mutate_app",
    "local_evolve_app",
    "remote_evolve_app",
    "local_extras_app",
    "remote_extras_app",
    "fetch_app",
    "local_db_app",
    "remote_db_app",
    "local_init_app",
    "remote_init_app",
    "local_process_app",
    "remote_process_app",
    "local_sort_app",
    "remote_sort_app",
    "remote_task_app",
    "local_analysis_app",
    "remote_analysis_app",
    "local_template_sets_app",
    "remote_template_sets_app",
    "local_validate_app",
    "remote_validate_app",
    "show_app",
    "dashboard_app",
    "local_publickey_app",
    "remote_publickey_app",
    "local_deploykey_app",
    "remote_deploykey_app",
    "local_secrets_app",
    "remote_secrets_app",
]
