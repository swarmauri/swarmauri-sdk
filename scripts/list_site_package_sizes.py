import subprocess
import os
import sys
import site
import importlib.util

def get_site_packages_path():
    """Automatically retrieve the path to the site-packages folder."""
    # Retrieve the path based on the current environment (system or virtual environment)
    paths = site.getsitepackages() if hasattr(site, 'getsitepackages') else [site.getusersitepackages()]
    # Choose the first path found for site-packages
    return paths[0]

def get_directory_size(path):
    """Calculate the directory size for a given path."""
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size

def format_size(bytes_size):
    """Convert size in bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"

def list_all_folder_sizes():
    """List sizes of all folders in the site-packages directory."""
    site_packages_path = get_site_packages_path()
    print(f"Site-packages directory: {site_packages_path}")
    
    for item in os.listdir(site_packages_path):
        item_path = os.path.join(site_packages_path, item)
        if os.path.isdir(item_path):
            size = get_directory_size(item_path)
            print(f"{item}: {format_size(size)}")

if __name__ == "__main__":
    list_all_folder_sizes()
