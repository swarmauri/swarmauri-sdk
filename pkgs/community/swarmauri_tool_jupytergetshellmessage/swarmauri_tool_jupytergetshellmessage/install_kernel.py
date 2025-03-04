from jupyter_client import KernelManager
import json
import subprocess


def is_kernel_available(kernel_name):
    result = subprocess.run(
        ["jupyter", "kernelspec", "list", "--json"], capture_output=True, text=True
    )
    kernels = json.loads(result.stdout).get("kernelspecs", {})
    return kernel_name in kernels


def ensure_kernel(kernel_name, display_name=None):
    """Ensure the Jupyter kernel exists; if not, install it."""
    # Get the list of existing kernels
    result = subprocess.run(
        ["jupyter", "kernelspec", "list", "--json"], capture_output=True, text=True
    )
    kernels = json.loads(result.stdout).get("kernelspecs", {})

    if kernel_name in kernels:
        print(f"Kernel '{kernel_name}' is already available.")
        return

    # Register the kernel
    display_name = display_name or f"Python ({kernel_name})"
    print(f"Installing kernel '{kernel_name}'...")
    subprocess.run(
        [
            "python",
            "-m",
            "ipykernel",
            "install",
            "--user",
            "--name",
            kernel_name,
            "--display-name",
            display_name,
        ],
        check=True,
    )

    print(f"Kernel '{kernel_name}' installed successfully.")


def main():
    """
    Ensure the custom kernel is available.
    """
    required_kernel = "my_kernel"

    ensure_kernel(required_kernel, "Python (Custom)")

    if not is_kernel_available(required_kernel):
        raise RuntimeError(
            f"Kernel '{required_kernel}' is not available. Please install it with 'python -m ipykernel install --user --name {required_kernel}'"
        )

    km = KernelManager(kernel_name=required_kernel)
    km.start_kernel()
