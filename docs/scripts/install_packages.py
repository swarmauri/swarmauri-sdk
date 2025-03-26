"""
This script installs packages in a directory using  pip install --no-deps .
It recursively processes directories to find and install packages.

"""

import os
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def is_package_installed(package_name):
    """Check if a package is already installed."""
    try:
        result = subprocess.run(
            ["pip", "show", package_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Error checking if package is installed: {e}")
        return False


def install_package(directory):
    """Install a package using pip install --no-deps ."""
    try:
        logging.info(f"Installing package in directory: {directory}")
        subprocess.run(["pip", "install", "--no-deps", "."], cwd=directory, check=True)
        logging.info(f"Successfully installed package in {directory}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install package in {directory}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while installing package in {directory}: {e}")


def process_directory(directory):
    """Recursively process directories to find and install packages concurrently."""
    try:
        tasks = []
        with ThreadPoolExecutor() as executor:
            for root, dirs, files in os.walk(directory):
                if "pyproject.toml" in files:
                    package_dir = root
                    package_name = os.path.basename(package_dir)
                    if not is_package_installed(package_name):
                        tasks.append(executor.submit(install_package, package_dir))
                    else:
                        logging.info(f"Package {package_name} is already installed.")

            for future in as_completed(tasks):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error in concurrent task: {e}")
    except Exception as e:
        logging.error(f"Error processing directory {directory}: {e}")


if __name__ == "__main__":
    # Replace 'your_directory_path' with the path to the directory you want to process
    your_directory_path = "../pkgs"
    process_directory(your_directory_path)
