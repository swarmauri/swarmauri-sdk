from __future__ import annotations

import asyncio
import typer

from peagen.tui.app import QueueDashboardApp

from peagen.defaults import DEFAULT_GATEWAY

# ────────────────────────── apps ───────────────────────────────


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
