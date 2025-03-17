import typer
import datetime
from colorama import Fore, Back, Style

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
    version_info = f"{Fore.CYAN}{Style.BRIGHT}Version: 0.1.0"
    tagline = f"{Fore.GREEN}{Style.BRIGHT}A Swarmauri scaffolding tool to simplify code gen."
    repo_info = Fore.YELLOW + "GitHub: https://github.com/swarmauri/swarmauri-sdk/pkgs/standards/ptree_dag" + Style.RESET_ALL
    usage_hint = f"{Fore.YELLOW}Type '--help' to see available commands."
    current_time = f"{Fore.MAGENTA}Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + Style.RESET_ALL

    # Print banner and additional information
    typer.echo(banner)
    typer.echo(version_info)
    typer.echo(tagline)
    typer.echo(repo_info)
    typer.echo(usage_hint)
    typer.echo(current_time)
    typer.echo()
