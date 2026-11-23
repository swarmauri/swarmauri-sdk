"""Open new files relative to trusted directory descriptors."""

import ctypes
import errno
import os
import platform
import sys
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
            opened = _linux_openat2(
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


def open_destination(target: Path, allowed_roots: list[str]) -> int:
    """Create exclusively beneath a configured root and return its descriptor.

    Directory capabilities remain anchored to the opened inodes. An external
    actor can rename those directories, but cannot redirect these handles by
    replacing their former pathnames with symlinks.
    """
    if "\x00" in str(target):
        raise ValueError("Destination must not contain NUL characters")
    if ".." in target.parts:
        raise ValueError("Parent traversal is not allowed")
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
        raise PermissionError(
            "Destination is outside configured allowed_roots"
        )

    root = max(roots, key=lambda candidate: len(candidate.parts))
    relative = target.relative_to(root)
    if not relative.parts:
        raise FileExistsError(errno.EEXIST, "Destination is an allowed root")
    if os.name == "nt":
        from . import _windows_fs

        return _windows_fs.open_file(
            root.anchor, root.parts[1:] + relative.parts, create=True
        )
    # A nested parent can move outside the root during Linux openat2(O_CREAT).
    if len(relative.parts) != 1:
        raise OSError(
            errno.ENOTSUP,
            "POSIX creation requires a direct child of a configured root",
        )
    directory_flags = _directory_flags()
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    root_fd = _open_root(root, directory_flags)
    try:
        return os.open(relative.name, flags, 0o666, dir_fd=root_fd)
    finally:
        os.close(root_fd)
