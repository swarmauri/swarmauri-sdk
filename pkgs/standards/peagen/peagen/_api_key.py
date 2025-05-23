"""Utility helpers for resolving API keys.

These functions inspect CLI options, ``.peagen.toml`` and environment
variables to determine the correct API key for an LLM provider.
"""

import os
import typer
from dotenv import load_dotenv
from pathlib import Path
import tomllib


def _resolve_api_key(
    provider: str,
    api_key: str = None,
    env_file: str = None,
) -> str:
    """
    Resolve the API key for a given provider in this order:
      1) CLI-provided api_key
      2) .peagen.toml under [llm.<provider>] api_key or API_KEY
      3) Environment variable: <PROVIDER>_API_KEY
    """

    # 1️⃣  CLI override
    if api_key:
        return api_key

    # 2️⃣  Try loading from .peagen.toml
    try:
        # walk up from cwd to find .peagen.toml
        toml_file = next(
            (
                d / ".peagen.toml"
                for d in [Path.cwd(), *Path.cwd().parents]
                if (d / ".peagen.toml").is_file()
            ),
            None,
        )
        if toml_file:
            with toml_file.open("rb") as f:
                data = tomllib.load(f)
            llm_conf = data.get("llm", {})
            prov_conf = llm_conf.get(provider, {}) or llm_conf.get(provider.lower(), {})
            toml_key = prov_conf.get("api_key") or prov_conf.get("API_KEY")
            if toml_key:
                return toml_key
    except Exception:
        # best-effort; fall back silently
        pass

    # 3️⃣  Fallback to environment
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    if not provider:
        typer.echo("[ERROR] --provider is required to resolve an API key.")
        raise typer.Exit(code=1)

    env_var = f"{provider.upper()}_API_KEY"
    env_key = os.getenv(env_var)
    if env_key:
        return env_key

    # 4️⃣  Nothing found — abort
    typer.echo(
        f"[ERROR] No API key found for provider '{provider}'.\n"
        f"Provide with --api-key, in .peagen.toml under [llm.{provider}].api_key, or via ${env_var}."
    )
    raise typer.Exit(code=1)
