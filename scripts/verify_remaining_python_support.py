"""Build and test the remaining Python support releases in isolated environments."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from poetry.core.masonry.api import build_wheel
from packaging.specifiers import SpecifierSet


def run(*args, **kwargs):
    subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def install_published_runtime(command, timeout=300, poll_seconds=10):
    """Require a successful index-only installation despite propagation delays."""
    deadline = time.monotonic() + timeout
    last_error = ""
    while time.monotonic() < deadline:
        result = subprocess.run(
            [str(arg) for arg in command], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(result.stdout, result.stderr, flush=True)
            return
        last_error = result.stdout + result.stderr
        print(last_error, flush=True)
        print("Waiting for a successful PyPI runtime installation", flush=True)
        time.sleep(poll_seconds)
    raise TimeoutError("PyPI runtime installation did not succeed: " + last_error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", action="store_true")
    parser.add_argument("--package")
    parser.add_argument(
        "--python", default=f"{sys.version_info.major}.{sys.version_info.minor}"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = root / "docs/releases/python-310-314-remaining-2026-11-19.json"
    release = json.loads(manifest.read_text(encoding="utf-8"))
    scope = release["scope"]
    packages = [p for p in scope if not args.package or p["name"] == args.package]
    if not packages:
        parser.error("Package is outside the release scope")
    if args.published and not args.package:
        parser.error(
            "Published verification requires one --package to preserve rollout order"
        )
    support = release["test_support"]
    output = (
        root
        / ".venv-remaining-compat"
        / args.python
        / ("published" if args.published else "candidate")
    )
    wheels = output / "dist"
    wheels.mkdir(parents=True, exist_ok=True)
    constraints = output / "constraints.txt"
    constraints.write_text(
        "\n".join(f"{p['name']}=={p['version']}" for p in scope + support)
        + "\nswarmauri_core==0.11.0.dev8\nswarmauri_base==0.11.0.dev13\n"
        + "swarmauri_standard==0.11.0.dev13\nswarmauri_transport_httpx==0.1.0.dev6\n",
        encoding="utf-8",
    )
    support_wheels = {}
    for package in support if args.published else scope + support:
        os.chdir(root / "pkgs" / package["member"])
        filename = build_wheel(str(wheels))
        support_wheels[package["name"]] = wheels / filename
    os.chdir(root)
    for package in packages:
        name = package["name"]
        member = root / "pkgs" / package["member"]
        with (member / "pyproject.toml").open("rb") as stream:
            metadata = tomllib.load(stream)
        environment = output / name / ("env-" + uuid4().hex)
        run("uv", "venv", environment, "--python", args.python)
        binaries = environment / ("Scripts" if sys.platform == "win32" else "bin")
        python = binaries / ("python.exe" if sys.platform == "win32" else "python")
        install = [
            "uv",
            "pip",
            "install",
            "--python",
            python,
            "--index-url",
            "https://pypi.org/simple/",
        ]
        development = metadata.get("dependency-groups", {}).get("dev", [])
        if args.published:
            # Install runtime solely from PyPI before introducing test fixtures.
            install_published_runtime(
                [*install, "--no-cache", "--refresh", f"{name}=={package['version']}"]
            )
        else:
            run(
                *install,
                "--find-links",
                wheels,
                "--constraint",
                constraints,
                f"{name}=={package['version']}",
                *development,
            )
        run("uv", "pip", "check", "--python", python)
        probe = subprocess.check_output(
            [
                str(python),
                "-I",
                "-c",
                f"import {name},json,sys; from pathlib import Path; "
                "from importlib.metadata import distribution; "
                f"assert Path({name}.__file__).is_relative_to(Path(sys.prefix)); "
                f"d=distribution('{name}'); "
                f"print(json.dumps(dict(module_file={name}.__file__,version=d.version,"
                "requires_python=d.metadata['Requires-Python'],"
                "classifiers=d.metadata.get_all('Classifier',[]))))",
            ],
            text=True,
        )
        installed = json.loads(probe)
        assert installed["version"] == package["version"]
        for supported in ("3.10", "3.11", "3.12", "3.13", "3.14"):
            assert SpecifierSet(installed["requires_python"]).contains(supported + ".0")
            assert (
                f"Programming Language :: Python :: {supported}"
                in installed["classifiers"]
            )
        if args.published:
            fixtures = [
                support_wheels[p["name"]]
                for p in support
                if any(
                    dep == p["name"] or dep.startswith(p["name"] + ">")
                    for dep in development
                )
            ]
            run(*install, *development, *fixtures)
            run("uv", "pip", "check", "--python", python)
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
        (output / (name + ".json")).write_text(
            json.dumps(
                {
                    "package": name,
                    "version": package["version"],
                    "python": args.python,
                    "runtime_source": "PyPI only"
                    if args.published
                    else "candidate wheel",
                    "installed": installed,
                    "tests": "passed",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
