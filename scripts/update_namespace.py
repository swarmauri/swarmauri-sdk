import os
import toml

# Path to the swarmauri pyproject.toml
NAMESPACE_PYPROJECT = "swarmauri/pyproject.toml"

# Directory containing first-class plugins
FIRST_CLASS_DIR = "pkgs/first_class"


def get_first_class_plugins():
    """Scan the first_class directory and return a list of plugin paths."""
    return [
        os.path.join(FIRST_CLASS_DIR, plugin)
        for plugin in os.listdir(FIRST_CLASS_DIR)
        if os.path.isdir(os.path.join(FIRST_CLASS_DIR, plugin))
    ]


def update_namespace_pyproject(plugins):
    """Update the namespace pyproject.toml to include all first-class plugins."""
    with open(NAMESPACE_PYPROJECT, "r") as f:
        pyproject = toml.load(f)

    for plugin in plugins:
        plugin_name = os.path.basename(plugin)
        pyproject["tool"]["poetry"]["dependencies"][plugin_name] = {
            "path": f"../{plugin}"
        }

    with open(NAMESPACE_PYPROJECT, "w") as f:
        toml.dump(pyproject, f)


if __name__ == "__main__":
    plugins = get_first_class_plugins()
    update_namespace_pyproject(plugins)
    print(f"Updated {NAMESPACE_PYPROJECT} with {len(plugins)} first-class plugins.")
