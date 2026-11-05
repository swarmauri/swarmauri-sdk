# /// script
# requires-python = ">=3.10"
# dependencies = ["packaging>=24.2", "tomli>=2; python_version < '3.11'"]
# ///
"""Run isolated, resumable package checks across Python versions using uv."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import fnmatch
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import subprocess
import sys
import time
import threading
import xml.etree.ElementTree as ET
import zipfile
from packaging.requirements import Requirement
from packaging.markers import default_environment

try:
    import tomllib
except ImportError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
WHEEL_LOCKS: dict[tuple, threading.Lock] = {}
WHEEL_RESULTS: dict[tuple, tuple[Path | None, int]] = {}
WHEEL_GUARD = threading.Lock()


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def discover(root: Path = ROOT) -> dict:
    paths = subprocess.check_output(
        ["git", "ls-files", "*pyproject.toml"], cwd=root, text=True
    ).splitlines()
    packages = {}
    for relative in paths:
        path = root / relative
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        if not project.get("name") or project.get("package") is False:
            continue
        if data.get("tool", {}).get("uv", {}).get("package") is False:
            continue
        packages[canonical(project["name"])] = (path.parent, data)
    files = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
    ).splitlines()
    for package, data in packages.values():
        digest = hashlib.sha256()
        prefix = package.relative_to(root).as_posix() + "/"
        for relative in files:
            if relative.startswith(prefix) and (root / relative).is_file():
                digest.update(relative.encode())
                digest.update((root / relative).read_bytes())
        data["_signature"] = digest.hexdigest()
    return packages


def test_directory(package: Path) -> Path | None:
    for relative in ("tests/unit", "tests"):
        path = package / relative
        if path.is_dir() and any(path.rglob("*.py")):
            return path
    return None


def test_status(code: int) -> str:
    return {0: "passed", 5: "no_tests_collected"}.get(code, "test_failed")


def test_counts(path: Path) -> dict:
    """Separate real tests from license items, including skip reasons."""
    counts = Counter()
    reasons = Counter()
    for case in ET.parse(path).iter("testcase"):
        kind = (
            "license"
            if "swarmauri_tests_pylicense:" in case.get("name", "")
            else "functional"
        )
        outcome = next(
            (
                tag
                for tag in ("failure", "error", "skipped")
                if case.find(tag) is not None
            ),
            "passed",
        )
        counts[f"{kind}_{outcome}"] += 1
        if outcome == "skipped":
            reasons[case.find("skipped").get("message", "")] += 1
    return {"counts": dict(counts), "skip_reasons": dict(reasons)}


def local_dependencies(name: str, packages: dict, version=None) -> list[Path]:
    """Install local runtime dependencies together instead of stale PyPI copies."""
    seen = set()
    paths = []
    target = default_environment()
    if version:
        target.update(python_version=version, python_full_version=version + ".0")

    def visit(key):
        if key in seen:
            return
        seen.add(key)
        path, data = packages[key]
        for requirement in data["project"].get("dependencies", []):
            parsed = Requirement(requirement)
            if parsed.marker and not parsed.marker.evaluate(target):
                continue
            dependency = canonical(parsed.name)
            if dependency in packages and local_version_matches(
                parsed, packages[dependency][1]
            ):
                visit(dependency)
        paths.append(path)

    visit(name)
    return paths


def local_version_matches(requirement, data):
    """Never force a checkout version outside a declared dependency range."""
    version = data["project"].get("version")
    return version is None or requirement.specifier.contains(version, prereleases=True)


def dev_requirements(data: dict, group="dev") -> list[str]:
    requirements = []
    for value in data.get("dependency-groups", {}).get(group, []):
        if isinstance(value, str):
            requirements.append(value)
        elif "include-group" in value:
            requirements.extend(dev_requirements(data, value["include-group"]))
    return requirements


def install_inputs(name, packages, version=None):
    dependencies = local_dependencies(name, packages, version)
    requirements = []
    for requirement in dev_requirements(packages[name][1]):
        match = re.match(r"[A-Za-z0-9_.-]+", requirement)
        dependency = canonical(match[0]) if match else ""
        if dependency in packages and local_version_matches(
            Requirement(requirement), packages[dependency][1]
        ):
            for path in local_dependencies(dependency, packages, version):
                if path not in dependencies:
                    dependencies.append(path)
        else:
            requirements.append(requirement)
    plugin = packages["swarmauri-tests-pylicense"][0]
    if plugin not in dependencies:
        dependencies.append(plugin)
    return dependencies, requirements


def signature(name, packages, version=None):
    dependencies, requirements = install_inputs(name, packages, version)
    signatures = {path: data["_signature"] for path, data in packages.values()}
    payload = ["runner-v2", requirements, [signatures[p] for p in dependencies]]
    return hashlib.sha256(json.dumps(payload).encode()).hexdigest()


def run_command(command, cwd, env, log, timeout):
    """Keep output in a per-stage log and terminate the tree on timeout."""
    with log.open("w", encoding="utf-8") as output:
        output.write(json.dumps(command) + "\n")
        output.flush()
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=os.name != "nt",
        )
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                import signal

                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return 124


def write_report(report, results):
    """Retry Windows replacement when a report reader briefly holds the file."""
    temporary = report.with_suffix(".tmp")
    temporary.write_text(json.dumps(results, indent=2), encoding="utf-8")
    for attempt in range(100):
        try:
            temporary.replace(report)
            return
        except PermissionError:
            if attempt == 99:
                raise
            time.sleep(0.02)


def universal_wheel(wheel):
    """Never share incorrectly tagged native extensions between interpreters."""
    if not wheel.name.endswith("-none-any.whl"):
        return False
    with zipfile.ZipFile(wheel) as archive:
        if any(
            name.endswith((".pyd", ".so", ".dll", ".dylib"))
            for name in archive.namelist()
        ):
            raise ValueError(f"Native library in universal wheel: {wheel}")
    return True


def package_wheel(path, data, version, interpreter, env, args):
    """Build universal Python wheels once; build native wheels per interpreter."""
    base_key = (canonical(data["project"]["name"]), data["_signature"])
    key = (*base_key, version)
    universal = (*base_key, "universal")
    with WHEEL_GUARD:
        lock = WHEEL_LOCKS.setdefault(base_key, threading.Lock())
    with lock:
        if universal in WHEEL_RESULTS:
            return WHEEL_RESULTS[universal]
        if key in WHEEL_RESULTS:
            return WHEEL_RESULTS[key]
        base = args.output / "wheels" / key[0] / key[1][:16]
        compatible = list(base.glob("*/*-none-any.whl"))
        if compatible and universal_wheel(compatible[0]):
            WHEEL_RESULTS[universal] = (compatible[0], 0)
            return WHEEL_RESULTS[universal]
        directory = base / version
        directory.mkdir(parents=True, exist_ok=True)
        wheels = list(directory.glob("*.whl"))
        if not wheels:
            command = [
                "uv",
                "build",
                "--no-sources",
                "--python",
                interpreter,
                "--wheel",
                "--out-dir",
                str(directory),
                str(path),
            ]
            code = run_command(
                command, ROOT, env, directory / "build.log", args.timeout
            )
            if code:
                WHEEL_RESULTS[key] = (None, code)
                return WHEEL_RESULTS[key]
            wheels = list(directory.glob("*.whl"))
        wheel = wheels[0]
        WHEEL_RESULTS[key] = (wheel, 0)
        if universal_wheel(wheel):
            WHEEL_RESULTS[universal] = (wheel, 0)
        return WHEEL_RESULTS[key]


def check(name, version, packages, args):
    package, data = packages[name]
    directory = args.output / version / name
    directory.mkdir(parents=True, exist_ok=True)
    result = {
        "package": name,
        "python": version,
        "path": str(package.relative_to(ROOT)),
        "status": "pending",
        "signature": signature(name, packages, version),
    }
    started = time.monotonic()
    environment_root = (args.output / "envs").resolve()
    environment = environment_root / version / name
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["UV_CACHE_DIR"] = str(ROOT / ".tmp" / "compatibility-clean-cache")
    env["UV_LINK_MODE"] = "copy"
    env["PATH"] = os.pathsep.join(
        [str(python.parent), *args.tool_path, env.get("PATH", "")]
    )
    env.pop("VIRTUAL_ENV", None)
    installed = (
        ROOT
        / ".tmp"
        / ("python315-core-" + version)
        / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    interpreter = str(installed) if installed.exists() else version
    if not environment.resolve().is_relative_to(environment_root):
        raise ValueError("Environment path must stay inside the validation directory")
    command = ["uv", "venv", "--clear", "--python", interpreter, str(environment)]
    code = run_command(command, ROOT, env, directory / "environment.log", args.timeout)
    if code:
        result.update(status="environment_failed", exit=code)
        return result
    dependencies, requirements = install_inputs(name, packages, version)
    by_path = {path: data for path, data in packages.values()}
    wheels = []
    for path in dependencies:
        wheel, code = package_wheel(
            path, by_path[path], version, interpreter, env, args
        )
        if code:
            result.update(
                status="build_failed", exit=code, dependency=str(path.relative_to(ROOT))
            )
            return result
        wheels.append(wheel)
    # Resolve declared ranges on this interpreter, without stale lockfile pins.
    command = [
        "uv",
        "pip",
        "install",
        "--python",
        str(python),
        "--upgrade",
        "--no-sources",
    ]
    command += [str(path) for path in wheels]
    if args.find_links:
        command += ["--find-links", str(args.find_links.resolve())]
    command += requirements + ["pytest>=8", "packaging>=24.2", "tomli>=2"]
    code = run_command(command, ROOT, env, directory / "install.log", args.timeout)
    if code:
        result.update(status="install_failed", exit=code)
    elif (tests := test_directory(package)) is None:
        result.update(status="no_tests", exit=0)
    else:
        command = [
            str(python),
            "-m",
            "pytest",
            str(tests),
            "-q",
            "--import-mode=importlib",
            "-m",
            "not i9n and not perf and not example",
            "--pylicense-package=" + data["project"]["name"],
            "-o",
            "cache_dir=" + str(directory / "cache"),
            "--basetemp",
            str(directory / "tmp"),
            "--junitxml",
            str(directory / "tests.xml"),
        ]
        code = run_command(
            command, ROOT / "pkgs", env, directory / "test.log", args.timeout
        )
        result.update(status=test_status(code), exit=code)
        if (directory / "tests.xml").exists():
            result.update(test_counts(directory / "tests.xml"))
            counts = result["counts"]
            if code == 0 and not any(k.startswith("functional_") for k in counts):
                result["status"] = "license_only"
            elif code == 0 and not counts.get("functional_passed"):
                result["status"] = "tests_skipped"
    result["seconds"] = round(time.monotonic() - started, 2)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filter", nargs="?", default="*")
    parser.add_argument(
        "--python", nargs="+", default=[f"3.{n}" for n in range(10, 16)]
    )
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument(
        "--output", type=Path, default=ROOT / ".tmp/compatibility-results"
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument(
        "--cases-from",
        type=Path,
        help="Run only package/version pairs in a JSON result list",
    )
    parser.add_argument(
        "--packages", nargs="+", help="Explicit package names instead of a glob"
    )
    parser.add_argument(
        "--tool-path",
        action="append",
        default=[],
        help="Extra directory for test prerequisites such as OpenSSL",
    )
    parser.add_argument(
        "--find-links",
        type=Path,
        help="Explicit dependency-wheel directory; recorded in the report",
    )
    args = parser.parse_args()
    if any(not re.fullmatch(r"3\.\d+", version) for version in args.python):
        parser.error("--python expects version labels such as 3.10 or 3.15")
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    context = {
        "platform": platform.platform(),
        "controller_python": sys.version,
        "arguments": sys.argv[1:],
        "dependency_wheels": {
            wheel.name: hashlib.sha256(wheel.read_bytes()).hexdigest()
            for wheel in (args.find_links.glob("*.whl") if args.find_links else [])
        },
    }
    (args.output / "context.json").write_text(
        json.dumps(context, indent=2), encoding="utf-8"
    )
    packages = discover()
    selected = [
        name
        for name in packages
        if (
            name in {canonical(n) for n in args.packages}
            if args.packages
            else fnmatch.fnmatch(name, args.filter)
        )
    ]
    if not selected:
        parser.error("No packages match the filter")
    report = args.output / "results.json"
    results = json.loads(report.read_text()) if args.resume and report.exists() else []
    results = [
        r
        for r in results
        if r.get("signature") == signature(r["package"], packages, r["python"])
    ]
    if args.retry_failed:
        results = [r for r in results if not r["status"].endswith("failed")]
    completed = {(r["package"], r["python"]) for r in results}
    requested_cases = (
        {
            (row["package"], row["python"])
            for row in json.loads(args.cases_from.read_text())
        }
        if args.cases_from
        else None
    )
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        tasks = {
            pool.submit(check, name, version, packages, args): (name, version)
            for name in selected
            for version in args.python
            if (name, version) not in completed
            and (requested_cases is None or (name, version) in requested_cases)
        }
        for task in as_completed(tasks):
            try:
                result = task.result()
            except Exception as exc:
                name, version = tasks[task]
                result = {
                    "package": name,
                    "python": version,
                    "signature": signature(name, packages, version),
                    "status": "runner_failed",
                    "error": str(exc),
                }
            results.append(result)
            case_report = (
                args.output / result["python"] / result["package"] / "result.json"
            )
            case_report.parent.mkdir(parents=True, exist_ok=True)
            case_report.write_text(json.dumps(result, indent=2), encoding="utf-8")
            write_report(report, results)
            print(
                len(results),
                result["python"],
                result["package"],
                result["status"],
                flush=True,
            )
    print(json.dumps(dict(Counter(r["status"] for r in results)), indent=2))
    return int(any(r["status"].endswith("failed") for r in results))


if __name__ == "__main__":
    sys.exit(main())
