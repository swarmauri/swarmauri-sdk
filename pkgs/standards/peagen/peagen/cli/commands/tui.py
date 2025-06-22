from __future__ import annotations

import asyncio
import typer

import peagen.defaults as defaults

from peagen.tui.app import QueueDashboardApp

DEFAULT_GATEWAY = defaults.CONFIG["gateway_url"].rsplit("/", 1)[0]


dashboard_app = typer.Typer(help="Launch the Textual dashboard to monitor tasks.")


@dashboard_app.command("tui")
def run_dashboard(
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY,
        "--gateway-url",
        help="Base URL of the Peagen gateway",
    ),
) -> None:
    """Start the dashboard pointed at ``gateway_url``."""
    try:
        QueueDashboardApp(gateway_url=gateway_url).run()
    except (asyncio.CancelledError, KeyboardInterrupt):
        raise typer.Exit(1)
