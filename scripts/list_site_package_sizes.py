import os
import site


def get_site_packages_path():
    """Automatically retrieve the path to the site-packages folder."""
    paths = (
        site.getsitepackages()
        if hasattr(site, "getsitepackages")
        else [site.getusersitepackages()]
    )
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
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"


def list_all_folder_sizes():
    """List sizes of all folders in the site-packages directory."""
    site_packages_path = get_site_packages_path()
    print(f"Site-packages directory: {site_packages_path}")

    package_sizes = {}

    for item in os.listdir(site_packages_path):
        item_path = os.path.join(site_packages_path, item)
        if os.path.isdir(item_path):
            size = get_directory_size(item_path)
            package_sizes[item] = size

    # Print alphabetically sorted list of packages
    print("\n\n\nAlphabetical List of Packages and Sizes:")
    for package, size in sorted(package_sizes.items()):
        print(f"{package}: {format_size(size)}")

    # Print size-based sorted list of packages in descending order
    print("\n\n\nPackages Sorted by Size (Largest to Smallest):")
    for package, size in sorted(
        package_sizes.items(), key=lambda item: item[1], reverse=True
    ):
        print(f"{package}: {format_size(size)}")


if __name__ == "__main__":
    list_all_folder_sizes()
