"""Open files relative to trusted directory descriptors."""

import ctypes
import errno
import os
import platform
import sys
from pathlib import Path

_RESOLVE_NO_MAGICLINKS = 0x02
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


def _linux_openat2(
    root_fd: int, relative: Path, flags: int, allow_symlinks: bool = False
) -> int | None:
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
        resolve=_RESOLVE_BENEATH
        | (_RESOLVE_NO_MAGICLINKS if allow_symlinks else _RESOLVE_NO_SYMLINKS),
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


def open_file(
    target: Path,
    allowed_roots: list[str],
    allow_symlinks: bool = False,
    allow_unrestricted_paths: bool = False,
) -> int:
    """Open a file through held directory handles."""
    if (
        not target.is_absolute()
        or ".." in target.parts
        or "\x00" in str(target)
    ):
        raise ValueError(
            "file_path must be absolute without NULs or parent traversal"
        )
    roots = []
    if allow_unrestricted_paths:
        roots = [Path(target.anchor)]
    else:
        if not allowed_roots:
            raise ValueError("allowed_roots must contain a trusted path")
        for spelling in allowed_roots:
            root = Path(spelling).expanduser()
            if not root.is_absolute() or ".." in root.parts:
                raise ValueError(
                    "allowed_roots must be absolute without parent traversal"
                )
            if target.is_relative_to(root):
                roots.append(root)
    if not roots:
        raise PermissionError("file_path is outside configured allowed_roots")
    root = max(roots, key=lambda candidate: len(candidate.parts))
    relative = target.relative_to(root)
    if os.name == "nt":
        if allow_symlinks:
            raise OSError(
                errno.ENOTSUP, "Symlink opt-in requires Linux openat2"
            )
        from . import _windows_fs

        return _windows_fs.open_file(
            root.anchor, root.parts[1:] + relative.parts
        )
    directory_flags = _directory_flags()
    root_fd = _open_root(root, directory_flags)
    try:
        flags = os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC
        if not allow_symlinks:
            flags |= os.O_NOFOLLOW
        descriptor = _linux_openat2(root_fd, relative, flags, allow_symlinks)
        if descriptor is None:
            if allow_symlinks:
                raise OSError(
                    errno.ENOTSUP, "Symlink opt-in requires Linux openat2"
                )
            if not relative.parts:
                return os.dup(root_fd)
            descriptor = _open_direct_child(root_fd, relative, flags)
        return descriptor
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise PermissionError(
                "file_path must not contain forbidden symlinks"
            ) from exc
        raise
    finally:
        os.close(root_fd)
