import argparse
import os
import logging
from .logging_utils import get_logger, SWARMAURI_LOG_LEVEL
import subprocess
from swarmauri.registry import list_registry
from swarmauri.plugin_manager import get_entry_points, determine_plugin_manager

env_level = os.getenv("SWARMAURI_LOG_LEVEL")
if env_level:
    try:
        level = int(env_level)
    except ValueError:
        level = SWARMAURI_LOG_LEVEL
    logging.basicConfig(level=level)
else:
    logging.basicConfig(level=SWARMAURI_LOG_LEVEL)
logger = get_logger(__name__)


def run_command(command):
    """
    Run a shell command and handle errors.
    """
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        logger.swarmauri(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        raise


def install_plugin(plugin_name, use_pip=False, use_poetry=False):
    """
    Install a plugin using pip or poetry.
    """
    if use_pip:
        logger.swarmauri(f"Installing plugin '{plugin_name}' using pip...")
        run_command(["pip", "install", plugin_name])
    elif use_poetry:
        logger.swarmauri(f"Adding plugin '{plugin_name}' using poetry...")
        run_command(["poetry", "add", plugin_name])
    else:
        logger.warning("Specify --use-pip or --use-poetry to install the plugin.")


def remove_plugin(plugin_name, use_pip=False, use_poetry=False):
    """
    Remove a plugin using pip or poetry.
    """
    if use_pip:
        logger.swarmauri(f"Removing plugin '{plugin_name}' using pip...")
        run_command(["pip", "uninstall", "-y", plugin_name])
    elif use_poetry:
        logger.swarmauri(f"Removing plugin '{plugin_name}' using poetry...")
        run_command(["poetry", "remove", plugin_name])
    else:
        logger.warning("Specify --use-pip or --use-poetry to remove the plugin.")


def validate_plugin(plugin_name):
    """
    Validate a plugin without registering it.
    """
    logger.swarmauri(f"Validating plugin: {plugin_name}")
    try:
        for entry_point in get_entry_points():
            if entry_point.name == plugin_name:
                plugin_class = entry_point.load()
                plugin_manager = determine_plugin_manager(entry_point)
                resource_kind = (
                    entry_point.group[len("swarmauri.") :]
                    if "." in entry_point.group
                    else None
                )
                plugin_manager.validate(
                    entry_point.name, plugin_class, resource_kind, None
                )
                logger.swarmauri(f"Plugin '{plugin_name}' validated successfully.")
                return
        logger.warning(f"Plugin '{plugin_name}' not found among entry points.")
    except Exception as e:
        logger.error(f"Validation failed for plugin '{plugin_name}': {e}")
        print(f"Validation failed: {e}")


def register_plugin(plugin_name):
    """
    Register a plugin in the registry.
    """
    logger.swarmauri(f"Registering plugin: {plugin_name}")
    try:
        for entry_point in get_entry_points():
            if entry_point.name == plugin_name:
                plugin_class = entry_point.load()
                plugin_manager = determine_plugin_manager(entry_point)
                resource_kind = (
                    entry_point.group[len("swarmauri.") :]
                    if "." in entry_point.group
                    else None
                )
                plugin_manager.register(entry_point.name, plugin_class, resource_kind)
                logger.swarmauri(f"Plugin '{plugin_name}' registered successfully.")
                return
        logger.warning(f"Plugin '{plugin_name}' not found among entry points.")
    except Exception as e:
        logger.error(f"Registration failed for plugin '{plugin_name}': {e}")
        print(f"Registration failed: {e}")


def list_plugins():
    """
    List all registered plugins.
    """
    logger.swarmauri("Listing all registered plugins...")
    plugins = list_registry()
    if not plugins:
        print("No plugins registered.")
    else:
        print("Registered plugins:")
        for resource_path, module_path in plugins.items():
            print(f"- {resource_path}: {module_path}")


def main():
    """
    Entry point for the Swarmauri CLI.
    """
    parser = argparse.ArgumentParser(
        description="Swarmauri CLI: Manage plugins and namespace components."
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands for the CLI")

    # Subcommand: Install Plugin
    install_parser = subparsers.add_parser("install", help="Install a new plugin.")
    install_parser.add_argument(
        "plugin_name", type=str, help="Name of the plugin to install."
    )
    install_parser.add_argument(
        "--use-pip", action="store_true", help="Install using pip."
    )
    install_parser.add_argument(
        "--use-poetry", action="store_true", help="Install using poetry."
    )

    # Subcommand: Remove Plugin
    remove_parser = subparsers.add_parser("remove", help="Remove a plugin.")
    remove_parser.add_argument(
        "plugin_name", type=str, help="Name of the plugin to remove."
    )
    remove_parser.add_argument(
        "--use-pip", action="store_true", help="Remove using pip."
    )
    remove_parser.add_argument(
        "--use-poetry", action="store_true", help="Remove using poetry."
    )

    # Subcommand: Validate Plugin
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a plugin without registering it."
    )
    validate_parser.add_argument(
        "plugin_name", type=str, help="Name of the plugin to validate."
    )

    # Subcommand: Register Plugin
    register_parser = subparsers.add_parser("register", help="Register a plugin.")
    register_parser.add_argument(
        "plugin_name", type=str, help="Name of the plugin to register."
    )

    # Subcommand: List Plugins
    subparsers.add_parser("list", help="List all registered plugins.")

    # Parse arguments and execute the appropriate function
    args = parser.parse_args()

    if args.command == "install":
        install_plugin(
            args.plugin_name, use_pip=args.use_pip, use_poetry=args.use_poetry
        )
    elif args.command == "remove":
        remove_plugin(
            args.plugin_name, use_pip=args.use_pip, use_poetry=args.use_poetry
        )
    elif args.command == "validate":
        validate_plugin(args.plugin_name)
    elif args.command == "register":
        register_plugin(args.plugin_name)
    elif args.command == "list":
        list_plugins()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
