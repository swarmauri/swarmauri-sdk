import os
import typer
from dotenv import load_dotenv


def _resolve_api_key(provider: str, api_key: str = None, env_file: str = None) -> str:
    """
    Resolve the API key for a given provider.
    If `api_key` is provided, we use that.
    Otherwise, we look for an environment variable: <PROVIDER>_API_KEY.
    Raises a typer.Exit with a special message if no key can be found.
    """

    if api_key:
        return api_key  # user provided via CLI

    if not provider:
        # If there's no provider, there's no way to deduce which env variable to read.
        typer.echo(
            "[ERROR] --provider is required to auto-resolve an API key from env."
        )
        raise typer.Exit(code=1)

    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    env_var_name = f"{provider.upper()}_API_KEY"
    env_key = os.getenv(env_var_name)

    if not env_key:
        typer.echo(
            f"[ERROR] No API key found for provider '{provider}'. "
            f"Expected environment variable '{env_var_name}'. "
            "Please provide --api-key or set the corresponding environment variable."
        )
        raise typer.Exit(code=1)

    return env_key
