# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Regenerate official Gensim 4.4.0 Cython sources for newer Python wheels.

This is an explicit local dependency workaround, not a replacement PyPI release.
Requires uv and a working native compiler toolchain.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    "https://files.pythonhosted.org/packages/1a/80/"
    "fe9d2e1ace968041814dbcfce4e8499a643a36c41267fa4b6c4f54cce420/"
    "gensim-4.4.0.tar.gz"
)
SOURCE_HASH = "a3f5b626da5518e79a479140361c663089fe7998df8ba52d56e1ded71ac5bdf5"
FASTSS = (
    "https://raw.githubusercontent.com/piskvorky/gensim/4.4.0/"
    "gensim/similarities/fastss.pyx"
)
FASTSS_HASH = "28ef4b96570b64b674959f7900cc8786ab22df0c5871b6b9c9ee75a8a0241d1e"


def download(url: str, expected: str, path: Path) -> None:
    """Fetch only an exact, checksum-pinned upstream input."""
    data = path.read_bytes() if path.exists() else b""
    if hashlib.sha256(data).hexdigest() != expected:
        with urlopen(url, timeout=120) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError(f"SHA-256 mismatch: {url}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", nargs="+", default=["3.14", "3.15"])
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / ".tmp/compatibility-dependency-wheels",
    )
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    work = (ROOT / ".tmp/gensim-compat").resolve()
    work.mkdir(parents=True, exist_ok=True)
    archive_path = work / "gensim-4.4.0.tar.gz"
    download(SOURCE, SOURCE_HASH, archive_path)
    source = work / "gensim-4.4.0"
    if not source.exists():
        with tarfile.open(archive_path) as archive:
            for member in archive.getmembers():
                if not (work / member.name).resolve().is_relative_to(work):
                    raise RuntimeError("Unsafe archive member path")
                if member.issym() or member.islnk():
                    raise RuntimeError("Unexpected archive link")
            archive.extractall(work)
    # Upstream's sdist omits this .pyx, although setup.py's regeneration path
    # requires it. Restore exactly the source from the matching upstream tag.
    download(FASTSS, FASTSS_HASH, source / "gensim/similarities/fastss.pyx")
    for pyx in source.rglob("*.pyx"):
        for suffix in (".c", ".cpp"):
            generated = pyx.with_suffix(suffix).resolve()
            if not generated.is_relative_to(source.resolve()):
                raise RuntimeError("Generated file outside the build source")
            generated.unlink(missing_ok=True)
    environment = os.environ.copy()
    environment["UV_CACHE_DIR"] = str(ROOT / ".tmp/release26-cache")
    if sys.platform == "win32":
        environment["CL"] = environment.get("CL", "") + " /DCYTHON_CCOMPLEX=0"
    records = []
    for index, interpreter in enumerate(args.python):
        venv = (work / f"environment-{index}").resolve()
        if not venv.is_relative_to(work):
            raise RuntimeError("Environment outside the task build directory")
        subprocess.run(
            ["uv", "venv", "--clear", "--python", interpreter, str(venv)],
            check=True,
            env=environment,
        )
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python),
                "Cython==3.3.1",
                "numpy==2.5.4",
                "scipy==1.18.1",
                "setuptools==84.2.1",
                "wheel==0.48.0",
            ],
            check=True,
            env=environment,
        )
        subprocess.run(
            [
                "uv",
                "build",
                "--python",
                str(python),
                "--no-build-isolation",
                "--wheel",
                "--out-dir",
                str(args.output),
                str(source),
            ],
            check=True,
            env=environment,
        )
        version = subprocess.check_output(
            [str(python), "--version"], text=True, env=environment
        ).strip()
        records.append({"interpreter": interpreter, "version": version})
    manifest = {
        "source": SOURCE,
        "source_sha256": SOURCE_HASH,
        "additional_source": FASTSS,
        "additional_source_sha256": FASTSS_HASH,
        "modifications": "Regenerated C/C++ using Cython 3.3.1; no algorithm changes",
        "builds": records,
        "wheels": {
            wheel.name: hashlib.sha256(wheel.read_bytes()).hexdigest()
            for wheel in args.output.glob("gensim-4.4.0-*.whl")
        },
    }
    (args.output / "gensim-build-provenance.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
