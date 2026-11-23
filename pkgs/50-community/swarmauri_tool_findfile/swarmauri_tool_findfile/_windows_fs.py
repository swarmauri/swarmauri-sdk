"""Open one Windows path component at a time from a held directory handle."""

import ctypes
import errno
from contextlib import contextmanager
from ctypes import wintypes

_kernel = ctypes.WinDLL("kernel32", use_last_error=True)
_nt = ctypes.WinDLL("ntdll")

_DIRECTORY = 0x10
_DEVICE = 0x40
_REPARSE = 0x400
_READ_ATTRIBUTES = 0x80
_SYNCHRONIZE = 0x100000
_TRAVERSE = 0x20
_LIST_DIRECTORY = 0x01
_SHARE_READ_WRITE = 0x3  # Omit FILE_SHARE_DELETE on handles we hold.
_FILE_OPEN = 1
_FILE_CREATE = 2
_DIRECTORY_FILE = 1
_NON_DIRECTORY_FILE = 0x40
_SYNCHRONOUS_NONALERT = 0x20
_OPEN_REPARSE_POINT = 0x200000
_OBJ_CASE_INSENSITIVE = 0x40
_OBJ_DONT_REPARSE = 0x1000
_OPEN_EXISTING = 3
_BACKUP_SEMANTICS = 0x02000000
_WIN32_OPEN_REPARSE_POINT = 0x00200000
_INVALID_HANDLE = ctypes.c_void_p(-1).value


class _UnicodeString(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.USHORT),
        ("MaximumLength", wintypes.USHORT),
        ("Buffer", wintypes.LPWSTR),
    ]


class _ObjectAttributes(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.ULONG),
        ("RootDirectory", wintypes.HANDLE),
        ("ObjectName", ctypes.POINTER(_UnicodeString)),
        ("Attributes", wintypes.ULONG),
        ("SecurityDescriptor", wintypes.LPVOID),
        ("SecurityQualityOfService", wintypes.LPVOID),
    ]


class _IoStatusBlock(ctypes.Structure):
    _fields_ = [
        ("StatusOrPointer", wintypes.LPVOID),
        ("Information", ctypes.c_size_t),
    ]


def _bind(library, name, result_type, *arg_types):
    function = getattr(library, name)
    function.argtypes = arg_types
    function.restype = result_type
    return function


_get_volume = _bind(
    _kernel,
    "GetVolumeNameForVolumeMountPointW",
    wintypes.BOOL,
    wintypes.LPCWSTR,
    wintypes.LPWSTR,
    wintypes.DWORD,
)
_create_file = _bind(
    _kernel,
    "CreateFileW",
    wintypes.HANDLE,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE,
)
_close = _bind(_kernel, "CloseHandle", wintypes.BOOL, wintypes.HANDLE)
_file_type = _bind(_kernel, "GetFileType", wintypes.DWORD, wintypes.HANDLE)
_file_info = _bind(
    _kernel,
    "GetFileInformationByHandleEx",
    wintypes.BOOL,
    wintypes.HANDLE,
    ctypes.c_int,
    wintypes.LPVOID,
    wintypes.DWORD,
)
_nt_create = _bind(
    _nt,
    "NtCreateFile",
    wintypes.LONG,
    ctypes.POINTER(wintypes.HANDLE),
    wintypes.DWORD,
    ctypes.POINTER(_ObjectAttributes),
    ctypes.POINTER(_IoStatusBlock),
    wintypes.LPVOID,
    wintypes.ULONG,
    wintypes.ULONG,
    wintypes.ULONG,
    wintypes.ULONG,
    wintypes.LPVOID,
    wintypes.ULONG,
)
_dos_error = _bind(
    _nt,
    "RtlNtStatusToDosError",
    wintypes.ULONG,
    wintypes.LONG,
)


def close_directory(handle: int) -> None:
    """Close a directory handle owned by the caller."""
    if not _close(handle):
        raise ctypes.WinError(ctypes.get_last_error())


def _validate_handle(handle: int, *, directory: bool) -> None:
    # FileAttributeTagInfo returns two DWORDs: attributes and reparse tag.
    info = (wintypes.DWORD * 2)()
    if not _file_info(handle, 9, info, ctypes.sizeof(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    attributes = info[0]
    if attributes & _REPARSE:
        raise PermissionError(
            errno.EACCES, "Windows reparse points and symlinks are forbidden"
        )
    if bool(attributes & _DIRECTORY) != directory:
        if directory:
            raise NotADirectoryError(errno.ENOTDIR, "Expected a directory")
        raise ValueError("Expected a regular file")
    if attributes & _DEVICE or _file_type(handle) != 1:  # FILE_TYPE_DISK
        raise ValueError("Expected a disk file or directory")


def _checked_handle(handle: int, *, directory: bool) -> int:
    try:
        _validate_handle(handle, directory=directory)
    except BaseException:
        close_directory(handle)
        raise
    return handle


def _open_volume(anchor: str, *, list_entries: bool) -> int:
    if (
        len(anchor) != 3
        or anchor[0]
        not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        or anchor[1:] != ":\\"
    ):
        raise ValueError(
            "Use an absolute drive-letter path on a local Windows volume"
        )
    volume = ctypes.create_unicode_buffer(64)
    if not _get_volume(anchor, volume, len(volume)):
        raise ctypes.WinError(ctypes.get_last_error())
    handle = _create_file(
        volume.value,
        _TRAVERSE
        | _READ_ATTRIBUTES
        | _SYNCHRONIZE
        | (_LIST_DIRECTORY if list_entries else 0),
        _SHARE_READ_WRITE,
        None,
        _OPEN_EXISTING,
        _BACKUP_SEMANTICS | _WIN32_OPEN_REPARSE_POINT,
        None,
    )
    if handle == _INVALID_HANDLE:
        raise ctypes.WinError(ctypes.get_last_error())
    return _checked_handle(handle, directory=True)


def _valid_component(name: str) -> bool:
    # Win32 interprets these basenames as devices even with extensions.
    stem = name.partition(".")[0].rstrip(" ").upper()
    reserved = stem in {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} or (
        len(stem) == 4
        and stem[:3] in {"COM", "LPT"}
        and stem[3] in "123456789¹²³"
    )
    return not (
        reserved
        or not name
        or name in {".", ".."}
        or name.endswith((" ", "."))
        or any(
            character in '\\/:*?"<>|' or ord(character) < 32
            for character in name
        )
    )


def _component_name(name: str) -> _UnicodeString:
    if not _valid_component(name):
        raise ValueError("Invalid Windows path component")
    raw = name.encode("utf-16-le", errors="surrogatepass")
    if len(raw) > 510:
        raise ValueError("Windows path component exceeds 255 UTF-16 units")
    # Pass counted UTF-16 directly, including non-BMP names.
    buffer = ctypes.create_string_buffer(raw + b"\0\0")
    return _UnicodeString(
        len(raw), len(raw) + 2, ctypes.cast(buffer, wintypes.LPWSTR)
    )


def _open_child(
    parent: int,
    name: str,
    *,
    directory: bool,
    create: bool = False,
    list_entries: bool = False,
) -> int:
    text = _component_name(name)
    attributes = _ObjectAttributes(
        ctypes.sizeof(_ObjectAttributes),
        parent,
        ctypes.pointer(text),
        _OBJ_CASE_INSENSITIVE | _OBJ_DONT_REPARSE,
        None,
        None,
    )
    access = _TRAVERSE if directory else (2 if create else 1)
    if list_entries:
        access |= _LIST_DIRECTORY
    kind = (
        _DIRECTORY_FILE
        if directory
        else (_NON_DIRECTORY_FILE if create else 0)
    )
    handle = wintypes.HANDLE()
    status = _nt_create(
        ctypes.byref(handle),
        access | _READ_ATTRIBUTES | _SYNCHRONIZE,
        ctypes.byref(attributes),
        ctypes.byref(_IoStatusBlock()),
        None,
        0,
        _SHARE_READ_WRITE,
        _FILE_CREATE if create else _FILE_OPEN,
        kind | _SYNCHRONOUS_NONALERT | _OPEN_REPARSE_POINT,
        None,
        0,
    )
    if status & 0xFFFFFFFF == 0xC000050B:
        raise PermissionError(
            errno.EACCES, "Windows reparse points are forbidden"
        )
    if status < 0:
        error = _dos_error(status)
        if error == 267:  # ERROR_DIRECTORY
            raise NotADirectoryError(
                errno.ENOTDIR, "Expected a directory", name
            )
        raise ctypes.WinError(error)
    return _checked_handle(handle.value, directory=directory)


@contextmanager
def _directories(anchor: str, parts: tuple[str, ...]):
    """Hold the volume and all traversed directories during the operation."""
    handles = [_open_volume(anchor, list_entries=not parts)]
    try:
        for index, part in enumerate(parts):
            handles.append(
                _open_child(
                    handles[-1],
                    part,
                    directory=True,
                    list_entries=index == len(parts) - 1,
                )
            )
        yield handles[-1]
    finally:
        for handle in reversed(handles):
            _close(handle)


@contextmanager
def directory(anchor: str, parts: tuple[str, ...]):
    """Yield the held directory handle for an anchored scan."""
    with _directories(anchor, parts) as handle:
        yield handle


def child_directory(parent: int, name: str) -> int:
    """Open a scanned directory by its name relative to the held parent."""
    return _open_child(parent, name, directory=True, list_entries=True)


def directory_entries(handle: int):
    """Stream records from the directory handle in bounded batches."""
    import stat
    import struct

    # FILE_FULL_DIR_INFO has an eight-byte aligned header and a UTF-16 name.
    # Use a bounded, explicitly aligned buffer for the packed record chain.
    buffer = (ctypes.c_uint64 * 8192)()
    info_class = 15  # FileFullDirectoryRestartInfo
    while _file_info(handle, info_class, buffer, ctypes.sizeof(buffer)):
        data = memoryview(buffer).cast("B")
        offset = 0
        while True:
            next_offset = struct.unpack_from("<I", data, offset)[0]
            attributes, length = struct.unpack_from("<II", data, offset + 56)
            name_start = offset + 68
            end = offset + next_offset if next_offset else len(data)
            if (
                end > len(data)
                or name_start + length > end
                or length % 2
                or (next_offset and next_offset % 8)
            ):
                raise OSError(errno.EIO, "Invalid Windows directory record")
            name = bytes(data[name_start : name_start + length]).decode(
                "utf-16-le", errors="surrogatepass"
            )
            if name not in {".", ".."}:
                if not _valid_component(name):
                    mode = None
                elif attributes & (_REPARSE | _DEVICE):
                    mode = 0
                else:
                    mode = (
                        stat.S_IFDIR
                        if attributes & _DIRECTORY
                        else stat.S_IFREG
                    )
                yield name, mode
            if not next_offset:
                break
            offset = end
        info_class = (
            14  # FileFullDirectoryInfo, continuing from the held cursor
        )
    error = ctypes.get_last_error()
    if error not in {18, 38}:  # ERROR_NO_MORE_FILES / ERROR_HANDLE_EOF
        raise ctypes.WinError(error)
