"""Scan directories through held filesystem handles and bound the response."""

import ctypes
import errno
import json
import time
import os
import platform
import sys
import stat
from contextlib import contextmanager
from pathlib import Path

_RESOLVE_NO_SYMLINKS = 0x04
_RESOLVE_BENEATH = 0x08
_OPENAT2_ARCHES = {
    "x86_64",
    "amd64",
    "i386",
    "i686",
    "aarch64",
    "arm64",
    "armv7l",
    "riscv64",
    "ppc64",
    "ppc64le",
    "s390x",
}


class _OpenHow(ctypes.Structure):
    _fields_ = [
        ("flags", ctypes.c_uint64),
        ("mode", ctypes.c_uint64),
        ("resolve", ctypes.c_uint64),
    ]


def _directory_flags() -> int:
    """Refuse platforms without descriptor-relative, no-symlink traversal."""
    if (
        os.open not in os.supports_dir_fd
        or not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
        or not hasattr(os, "O_CLOEXEC")
    ):
        raise OSError(
            errno.ENOTSUP,
            "This platform lacks secure directory-relative file creation",
        )
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


def _open_root(root: Path, directory_flags: int) -> int:
    """Anchor a trusted absolute root without following any symlink."""
    descriptor = os.open(root.anchor, directory_flags)
    try:
        if root.parts[1:]:
            opened = _open_root_beneath(
                descriptor, Path(*root.parts[1:]), directory_flags
            )
            if opened is not None:
                os.close(descriptor)
                return opened
        for part in root.parts[1:]:
            child = os.open(part, directory_flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _linux_openat2(root_fd: int, relative: Path, flags: int) -> int | None:
    """Use kernel-enforced resolution, or signal that it is unavailable."""
    if (
        sys.platform != "linux"
        or platform.machine().lower() not in _OPENAT2_ARCHES
    ):
        return None
    libc = ctypes.CDLL(None, use_errno=True)
    syscall = libc.syscall
    syscall.restype = ctypes.c_long
    how = _OpenHow(
        flags=flags,
        mode=0,
        resolve=_RESOLVE_BENEATH | _RESOLVE_NO_SYMLINKS,
    )
    result = syscall(
        ctypes.c_long(437),
        ctypes.c_int(root_fd),
        ctypes.c_char_p(os.fsencode(relative)),
        ctypes.byref(how),
        ctypes.c_size_t(ctypes.sizeof(how)),
    )
    if result >= 0:
        return int(result)
    code = ctypes.get_errno()
    if code in {errno.ENOSYS, errno.EINVAL, errno.E2BIG}:
        return None
    raise OSError(code, os.strerror(code), str(relative))


# Root establishment and operation lookup use the same kernel primitive.
_open_root_beneath = _linux_openat2


def _open_direct_child(root_fd: int, relative: Path, flags: int) -> int:
    """Use a single no-follow lookup when kernel containment is unavailable."""
    if len(relative.parts) != 1:
        raise OSError(errno.ENOTSUP, "Nested paths require Linux openat2")
    return os.open(relative.name, flags, 0o666, dir_fd=root_fd)


@contextmanager
def open_directory(target: Path, allowed_roots: list[str]):
    """Open beneath a trusted root without following any symlink."""
    if "\x00" in str(target) or ".." in target.parts:
        raise ValueError("NUL characters and parent traversal are not allowed")
    if not allowed_roots:
        raise ValueError("allowed_roots must contain a trusted directory")
    roots = []
    for spelling in allowed_roots:
        root = Path(spelling).expanduser()
        if not root.is_absolute() or ".." in root.parts:
            raise ValueError(
                "allowed_roots must be absolute without parent traversal"
            )
        if target.is_relative_to(root):
            roots.append(root)
    if not roots:
        raise PermissionError("Path is outside configured allowed_roots")
    root = max(roots, key=lambda candidate: len(candidate.parts))
    relative = target.relative_to(root)
    if os.name == "nt":
        from . import _windows_fs

        with _windows_fs.directory(
            root.anchor, root.parts[1:] + relative.parts
        ) as handle:
            yield handle, None, Path()
        return

    flags = _directory_flags()
    root_fd = _open_root(root, flags)
    try:
        with _scan_posix(root_fd, relative) as descriptor:
            yield descriptor, root_fd, relative
    finally:
        os.close(root_fd)


@contextmanager
def _scan_posix(root_fd: int, relative: Path):
    """Open and recheck each scanned directory against the original root."""
    if not relative.parts:
        yield root_fd
        return

    def lookup():
        flags = _directory_flags()
        descriptor = _linux_openat2(root_fd, relative, flags)
        return (
            _open_direct_child(root_fd, relative, flags)
            if descriptor is None
            else descriptor
        )

    descriptor = lookup()
    try:
        yield descriptor
        current = lookup()
        try:
            if not os.path.samestat(os.fstat(descriptor), os.fstat(current)):
                raise PermissionError("Directory changed during scan")
        finally:
            os.close(current)
    finally:
        os.close(descriptor)


@contextmanager
def child_directory(
    parent_fd: int, name: str, root_fd: int | None, relative: Path
):
    """Open from the original POSIX root or the held Windows parent."""
    if root_fd is not None:
        with _scan_posix(root_fd, relative) as descriptor:
            yield descriptor
        return

    from . import _windows_fs

    handle = _windows_fs.child_directory(parent_fd, name)
    try:
        yield handle
    finally:
        _windows_fs.close_directory(handle)


def directory_entries(descriptor: int):
    """Yield entry names and types without following links."""
    if os.name == "nt":
        from . import _windows_fs

        yield from _windows_fs.directory_entries(descriptor)
        return
    with os.scandir(descriptor) as children:
        for child in children:
            yield (
                child.name,
                stat.S_IFMT(child.stat(follow_symlinks=False).st_mode),
            )


class Budget:
    """Bound entries, retained JSON output, and scan time."""

    def __init__(self, scanned: int, results: int, size: int, seconds: float):
        self.max_scanned = scanned
        self.max_results = results
        self.max_bytes = size
        self.deadline = time.monotonic() + seconds
        self.scanned = 0
        self.results = 0
        self.size = 0

    def check(self) -> None:
        if time.monotonic() > self.deadline:
            raise ValueError("Scan exceeded the elapsed-time limit")

    def visit(self) -> None:
        self.check()
        self.scanned += 1
        if self.scanned > self.max_scanned:
            raise ValueError("Scan exceeded the scanned-entry limit")

    def retain(self, item: object) -> None:
        self.check()
        self.results += 1
        self.size += (
            len(json.dumps(item, ensure_ascii=True).encode("utf-8")) + 2
        )
        if self.results > self.max_results:
            raise ValueError("Scan exceeded the result limit")
        if self.size > self.max_bytes:
            raise ValueError("Scan exceeded the returned-byte limit")

    def finish(self, result: dict) -> None:
        self.check()
        if (
            len(json.dumps(result, ensure_ascii=True).encode("utf-8"))
            > self.max_bytes
        ):
            raise ValueError("Scan exceeded the returned-byte limit")
        self.check()


def failure_response(result: dict, limit: int) -> dict:
    """Bound echoed input and diagnostic output, retaining a useful error."""
    # Keep room for a structured error even with tiny success budgets.
    limit = max(256, min(limit, 4096))
    for key, value in result.items():
        if isinstance(value, str) and len(value) > limit:
            result[key] = value[: limit - 3] + "..."
    while len(json.dumps(result, ensure_ascii=True).encode("utf-8")) > limit:
        key = max(
            (key for key, value in result.items() if isinstance(value, str)),
            key=lambda key: len(result[key]),
        )
        result[key] = result[key][: len(result[key]) // 2]
    return result
