"""Bundle a checksum-pinned upstream shared library for the ctypes provider."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
from urllib.request import urlopen
import zipfile

VERSION = "1.0.22"
HASHES = {
    "msvc.zip": (
        "3e03a726fac4bc09cb61d8f29d658ef7a5eca0811de59082130414f7ca2e4279"
    ),
    "tar.gz": (
        "adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349"
    ),
}


def bundle(output: Path) -> Path:
    """Bundle upstream Windows DLLs or compile the Unix shared library."""
    output.mkdir(parents=True, exist_ok=True)
    suffix = "msvc.zip" if sys.platform == "win32" else "tar.gz"
    name = (
        f"libsodium-{VERSION}-{suffix}"
        if suffix == "msvc.zip"
        else f"libsodium-{VERSION}.{suffix}"
    )
    cache = (
        Path(os.environ.get("UV_CACHE_DIR", tempfile.gettempdir()))
        / "swarmauri-libsodium"
    )
    cache.mkdir(parents=True, exist_ok=True)
    cached = cache / name
    data = cached.read_bytes() if cached.exists() else b""
    if hashlib.sha256(data).hexdigest() != HASHES[suffix]:
        with urlopen(
            f"https://download.libsodium.org/libsodium/releases/{name}",
            timeout=120,
        ) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != HASHES[suffix]:
            raise RuntimeError(
                "Upstream libsodium archive failed SHA-256 verification"
            )
        # Separate temporary files keep concurrent Python-version builds safe.
        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as temporary:
            temporary.write(data)
            temporary_path = Path(temporary.name)
        temporary_path.replace(cached)
    if sys.platform == "win32":
        architectures = {
            "amd64": "x64",
            "x86_64": "x64",
            "x86": "Win32",
            "arm64": "ARM64",
            "aarch64": "ARM64",
        }
        architecture = architectures[platform.machine().lower()]
        destination = output / "libsodium.dll"
        with zipfile.ZipFile(cached) as archive:
            destination.write_bytes(
                archive.read(
                    f"libsodium/{architecture}/Release/v143/dynamic/libsodium.dll"
                )
            )
        return destination
    with tempfile.TemporaryDirectory(
        prefix="swarmauri-libsodium-"
    ) as temporary:
        source_root = Path(temporary)
        with tarfile.open(cached) as archive:
            for member in archive.getmembers():
                target = (source_root / member.name).resolve()
                if not target.is_relative_to(source_root.resolve()):
                    raise RuntimeError("Unsafe path in libsodium archive")
                if member.issym() or member.islnk():
                    raise RuntimeError("Unexpected link in libsodium archive")
            archive.extractall(source_root)
        source = source_root / f"libsodium-{VERSION}"
        prefix = source_root / "installed"
        subprocess.run(
            [
                "sh",
                "configure",
                "--enable-shared",
                "--disable-static",
                f"--prefix={prefix}",
            ],
            cwd=source,
            check=True,
            stdout=sys.stderr,
        )
        subprocess.run(
            ["make", "-j2"], cwd=source, check=True, stdout=sys.stderr
        )
        subprocess.run(
            ["make", "install"], cwd=source, check=True, stdout=sys.stderr
        )
        pattern = (
            "libsodium.*.dylib"
            if sys.platform == "darwin"
            else "libsodium.so.*.*.*"
        )
        library = next((prefix / "lib").glob(pattern))
        destination = output / (
            "libsodium.dylib" if sys.platform == "darwin" else "libsodium.so"
        )
        shutil.copy2(library.resolve(), destination)
        return destination


if __name__ == "__main__":
    print(bundle(Path(sys.argv[1]).resolve()))
