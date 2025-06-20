from __future__ import annotations

import typer

from peagen.tui.app import QueueDashboardApp

DEFAULT_GATEWAY = "http://localhost:8000"


dashboard_app = typer.Typer(help="Launch the Textual dashboard to monitor tasks.")


@dashboard_app.command("tui")
def run_dashboard(
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY,
        "--gateway-url",
        help="Base URL of the Peagen gateway",
    )
) -> None:
    """Start the dashboard pointed at ``gateway_url``."""
    QueueDashboardApp(gateway_url=gateway_url).run()

