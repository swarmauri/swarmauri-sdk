import logging
import os
import platform
import sys
from datetime import datetime
from IPython import get_ipython
from urllib.parse import unquote

try:
    import tomllib
except ImportError:
    import tomli as tomllib


_cached_version = None


def get_version_from_pyproject():
    global _cached_version
    if _cached_version is not None:
        return _cached_version

    pyproject_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "swarmauri/pyproject.toml"
    )
    logging.info(f"Reading Swarmauri version from {pyproject_path}")
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        version = data.get("tool", {}).get("poetry", {}).get("version")
        if version is None:
            version = data.get("project", {}).get("version", "development")
        _cached_version = version
        return version
    except Exception:
        _cached_version = "Swarmauri version information is unavailable. Ensure it is installed properly."
        return _cached_version


def get_notebook_name():
    """
    Returns the name of the current Jupyter notebook file when running.
    Returns None if not running in a notebook or if the name cannot be determined.
    """
    try:
        ipython = get_ipython()
        if ipython is None or not hasattr(ipython, "kernel"):
            return None

        kernel = ipython.kernel

        if hasattr(kernel, "get_parent"):
            parent = kernel.get_parent()
            metadata = parent.get("metadata", {}) if parent else {}
        else:
            metadata = {}

        def clean_filename(path):
            if not path:
                return None
            filename = os.path.basename(path)
            filename = filename.split("#")[0]
            filename = filename.split("?")[0]
            filename = unquote(filename)
            if filename.endswith(".ipynb"):
                return filename
            return None

        for field in ["filename", "originalPath", "path"]:
            if field in metadata:
                clean_name = clean_filename(metadata[field])
                if clean_name:
                    return clean_name

        cell_id = metadata.get("cellId", "")
        if cell_id and ".ipynb" in cell_id:
            notebook_parts = [part for part in cell_id.split("/") if ".ipynb" in part]
            if notebook_parts:
                clean_name = clean_filename(notebook_parts[0])
                if clean_name:
                    return clean_name
    except Exception as e:
        print(f"Error getting notebook name: {str(e)}")
        return None


def print_notebook_metadata(author_name, github_username):
    print(f"Author: {author_name}")
    print(f"GitHub Username: {github_username}")

    notebook_file = get_notebook_name()

    if notebook_file:
        try:
            last_modified_time = os.path.getmtime(notebook_file)
            last_modified_datetime = datetime.fromtimestamp(last_modified_time)
            print(f"Notebook File: {notebook_file}")
            print(f"Last Modified: {last_modified_datetime}")
        except Exception as e:
            print(f"Could not retrieve last modified datetime: {e}")
    else:
        print("Could not detect the current notebook's filename.")

    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")

    swarmauri_version = get_version_from_pyproject()
    print(f"Swarmauri Version: {swarmauri_version}")
