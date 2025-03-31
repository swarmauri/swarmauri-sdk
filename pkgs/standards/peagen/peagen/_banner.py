from ._config import __version__, __package_name__
import typer
import datetime
from colorama import Fore, Style


def _print_banner():
    # ASCII art banner
    banner = """
                                                                                                 ███ 
                                                                                                ░░░  
      █████  █████ ███ █████  ██████   ████████  █████████████    ██████   █████ ████ ████████  ████ 
     ███░░  ░░███ ░███░░███  ░░░░░███ ░░███░░███░░███░░███░░███  ░░░░░███ ░░███ ░███ ░░███░░███░░███ 
    ░░█████  ░███ ░███ ░███   ███████  ░███ ░░░  ░███ ░███ ░███   ███████  ░███ ░███  ░███ ░░░  ░███ 
     ░░░░███ ░░███████████   ███░░███  ░███      ░███ ░███ ░███  ███░░███  ░███ ░███  ░███      ░███ 
     ██████   ░░████░████   ░░████████ █████     █████░███ █████░░████████ ░░████████ █████     █████
    ░░░░░░     ░░░░ ░░░░     ░░░░░░░░ ░░░░░     ░░░░░ ░░░ ░░░░░  ░░░░░░░░   ░░░░░░░░ ░░░░░     ░░░░░ 
                                                                                                     
                                                                                                     
                                                                                                     
    """
    # Additional details
    version_info = f"{Fore.CYAN}{Style.BRIGHT}Version: {__version__}"
    package_info = (
        f"{Fore.BLUE}{Style.BRIGHT}Package Name: {__package_name__}{Style.RESET_ALL}"
    )
    tagline = (
        f"{Fore.GREEN}{Style.BRIGHT}A Swarmauri scaffolding tool to simplify code gen."
    )
    repo_info = (
        Fore.YELLOW
        + "GitHub: https://github.com/swarmauri/swarmauri-sdk/pkgs/standards/ptree_dag"
        + Style.RESET_ALL
    )
    usage_hint = f"{Fore.YELLOW}Type '--help' to see available commands."
    current_time = (
        f"{Fore.MAGENTA}Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        + Style.RESET_ALL
    )

    # Print banner and additional information
    typer.echo(banner)
    typer.echo(package_info)
    typer.echo(version_info)
    typer.echo(tagline)
    typer.echo(repo_info)
    typer.echo(usage_hint)
    typer.echo(current_time)
    typer.echo()
