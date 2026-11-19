"""Build and test the remaining Python support releases in isolated environments."""

import json
import os
from pathlib import Path
import subprocess
import sys

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from poetry.core.masonry.api import build_wheel


def run(*args, **kwargs):
    subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = root / "docs/releases/python-310-314-remaining-2026-11-19.json"
    release = json.loads(manifest.read_text(encoding="utf-8"))
    packages = release["scope"]
    support = release["test_support"]
    output = (
        root
        / ".venv-remaining-compat"
        / f"{sys.version_info.major}.{sys.version_info.minor}"
    )
    wheels = output / "dist"
    wheels.mkdir(parents=True, exist_ok=True)
    constraints = output / "constraints.txt"
    constraints.write_text(
        "\n".join(f"{p['name']}=={p['version']}" for p in packages + support)
        + "\nswarmauri_core==0.11.0.dev8\nswarmauri_base==0.11.0.dev13\n"
        + "swarmauri_standard==0.11.0.dev13\nswarmauri_transport_httpx==0.1.0.dev6\n",
        encoding="utf-8",
    )
    for package in packages + support:
        os.chdir(root / "pkgs" / package["member"])
        build_wheel(str(wheels))
    os.chdir(root)
    for package in packages:
        name = package["name"]
        member = root / "pkgs" / package["member"]
        with (member / "pyproject.toml").open("rb") as stream:
            metadata = tomllib.load(stream)
        environment = output / name
        run("uv", "venv", environment, "--python", sys.executable)
        binaries = environment / ("Scripts" if sys.platform == "win32" else "bin")
        python = binaries / ("python.exe" if sys.platform == "win32" else "python")
        run(
            "uv",
            "pip",
            "install",
            "--python",
            python,
            "--find-links",
            wheels,
            "--constraint",
            constraints,
            f"{name}=={package['version']}",
            *metadata.get("dependency-groups", {}).get("dev", []),
        )
        run("uv", "pip", "check", "--python", python)
        run(
            python,
            "-I",
            "-c",
            f"import {name},sys; from pathlib import Path; "
            f"assert Path({name}.__file__).is_relative_to(Path(sys.prefix))",
        )
        run(
            python,
            "-I",
            "-m",
            "pytest",
            "--import-mode=importlib",
            "-q",
            "-m",
            "not i9n and not live",
            "--junitxml=" + str(output / (name + ".xml")),
            member / "tests",
            cwd=member,
        )


if __name__ == "__main__":
    main()
