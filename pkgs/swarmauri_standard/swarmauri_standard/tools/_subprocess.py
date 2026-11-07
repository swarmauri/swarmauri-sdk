"""Execute subprocesses for the kernel and standalone tool surfaces."""

import ctypes
import locale
import os
import shlex
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Union


def _windows_executable(command: str) -> str:
    """Select a native image with the documented CreateProcess search order."""
    from _winapi import GetModuleFileName

    def directory(query) -> Path:
        buffer = ctypes.create_unicode_buffer(32768)
        length = query(buffer, len(buffer))
        if not 0 < length < len(buffer):
            raise ctypes.WinError(ctypes.get_last_error())
        return Path(buffer.value)

    candidate = Path(command)
    bare = candidate.name == command
    if bare and not candidate.suffix and not command.endswith("."):
        candidate = candidate.with_suffix(".exe")
    if candidate.suffix.lower() not in {".exe", ".com"}:
        raise ValueError("Windows shell=False requires a native .exe or .com")

    if bare:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        windows = directory(kernel.GetWindowsDirectoryW)
        folders = [
            Path(GetModuleFileName(0)).parent,
            Path.cwd(),
            directory(kernel.GetSystemDirectoryW),
            windows / "System",
            windows,
            *(
                Path(path.strip('"'))
                for path in os.environ.get("PATH", "").split(os.pathsep)
                if path
            ),
        ]
        matches = (folder / candidate for folder in folders)
    else:
        matches = iter((candidate,))

    for match in matches:
        if match.is_file():
            image = match.resolve(strict=True)
            if image.suffix.lower() not in {".exe", ".com"}:
                raise ValueError(
                    "Windows shell=False requires a native .exe or .com"
                )
            return str(image)
    raise FileNotFoundError(command)


def _read_windows_capture(capture) -> str:
    """Read a bounded snapshot without disturbing an inherited write offset."""
    size = os.fstat(capture.fileno()).st_size
    descriptor = os.open(
        capture.name, os.O_RDONLY | os.O_BINARY | os.O_TEMPORARY
    )
    with os.fdopen(descriptor, "rb") as reader:
        data = reader.read(size)
    encoding = (
        "utf-8" if sys.flags.utf8_mode else locale.getpreferredencoding(False)
    )
    return data.decode(encoding).replace("\r\n", "\n").replace("\r", "\n")


def run_subprocess(
    command: Union[str, List[str]],
    timeout: Optional[float] = None,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Union[str, int, None]]:
    """Run a command with the shared platform and result policies."""
    try:
        args: Union[str, List[str]]
        if isinstance(command, str):
            args = command if shell else shlex.split(command)
        elif isinstance(command, list):
            if shell:
                raise ValueError("shell=True requires a command string")
            if not all(isinstance(arg, str) for arg in command):
                raise ValueError("command arguments must be strings")
            args = command
        else:
            raise ValueError("command must be a string or argument list")
        if not args:
            raise ValueError("command must not be empty")

        executable = None
        if os.name == "nt" and not shell:
            executable = _windows_executable(args[0])

        options = {
            "executable": executable,
            "shell": shell,
            "timeout": timeout,
            "cwd": cwd,
            "env": env,
        }
        if os.name == "nt" and timeout is not None:
            with (
                NamedTemporaryFile() as stdout,
                NamedTemporaryFile() as stderr,
            ):
                result = subprocess.run(
                    args, stdout=stdout, stderr=stderr, **options
                )
                result.stdout = _read_windows_capture(stdout)
                result.stderr = _read_windows_capture(stderr)
        else:
            result = subprocess.run(
                args, capture_output=True, text=True, **options
            )
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "stdout": "",
            "stderr": f"Process timed out after {timeout} seconds",
            "exit_code": None,
        }
    except FileNotFoundError:
        return {
            "status": "not_found",
            "stdout": "",
            "stderr": (
                "Executable not found: "
                f"{args[0] if isinstance(args, list) else args}"
            ),
            "exit_code": 127,
        }
    except Exception as e:
        return {
            "status": "runtime_error",
            "stdout": "",
            "stderr": str(e),
            "exit_code": None,
        }
