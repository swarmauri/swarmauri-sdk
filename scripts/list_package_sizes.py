import subprocess
import os
import sys

def get_installed_packages():
    """Retrieve a list of installed packages with their names."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=freeze"],
        capture_output=True,
        text=True
    )
    packages = result.stdout.strip().splitlines()
    return [pkg.split("==")[0] for pkg in packages if "==" in pkg]

def get_package_location(package_name):
    """Retrieve the installation path of a given package using pip show."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", package_name],
        capture_output=True,
        text=True
    )
    for line in result.stdout.splitlines():
        if line.startswith("Location:"):
            return line.split(":", 1)[1].strip()
    return None

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

def list_package_sizes():
    """List sizes of installed packages."""
    packages = get_installed_packages()
    for package in packages:
        location = get_package_location(package)
        if location and os.path.isdir(os.path.join(location, package)):
            package_path = os.path.join(location, package)
            size = get_directory_size(package_path)
            print(f"{package}: {format_size(size)}")
        else:
            print(f"Could not determine path or size for package: {package}")

if __name__ == "__main__":
    list_package_sizes()
