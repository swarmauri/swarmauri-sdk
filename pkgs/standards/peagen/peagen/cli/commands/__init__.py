"""Expose all Typer sub-applications for the CLI."""

from .doe import local_doe_app, remote_doe_app
from .eval import local_eval_app, remote_eval_app
from .extras import local_extras_app, remote_extras_app
from .fetch import local_fetch_app, remote_fetch_app
from .db import local_db_app
from .init import local_init_app, remote_init_app
from .process import local_process_app, remote_process_app
from .mutate import local_mutate_app, remote_mutate_app
from .evolve import local_evolve_app, remote_evolve_app
from .sort import local_sort_app, remote_sort_app
from .task import remote_task_app
from .analysis import local_analysis_app, remote_analysis_app
from .templates import local_template_sets_app, remote_template_sets_app
from .tui import dashboard_app
from .validate import local_validate_app, remote_validate_app
from .login import login_app
from .keys import keys_app
from .secrets import local_secrets_app, remote_secrets_app
from .deploy import deploy_app

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
    "local_fetch_app",
    "remote_fetch_app",
    "local_db_app",
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
    "dashboard_app",
    "login_app",
    "keys_app",
    "local_secrets_app",
    "remote_secrets_app",
    "deploy_app",
]
