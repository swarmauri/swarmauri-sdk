import os
import site


def get_site_packages_path():
    """Retrieve the path to the site-packages directory."""
    return site.getsitepackages()[0] if site.getsitepackages() else None


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
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"


def calculate_total_site_packages_size():
    """Calculate and print the total size of all packages in site-packages."""
    site_packages_path = get_site_packages_path()
    if not site_packages_path or not os.path.isdir(site_packages_path):
        print("Could not determine the site-packages path.")
        return

    total_size = get_directory_size(site_packages_path)
    print(f"Total size of all packages in site-packages: {format_size(total_size)}")


if __name__ == "__main__":
    calculate_total_site_packages_size()
