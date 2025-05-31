from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional, ClassVar

import fsspec
import s3fs
from pydantic import PrivateAttr

from swarmauri_base.programs.ProgramBase import ProgramBase


class MemoryS3FSProgram(ProgramBase):
    """Program backed by an in-memory S3 filesystem."""

    _program_type: ClassVar[str] = "memory-s3fs"
    type: str = "MemoryS3FSProgram"
    id: str
    version: str
    metadata: Dict[str, Any]
    content: Dict[str, str]
    bucket: Optional[str] = None
    prefix: str = ""

    _fs: s3fs.S3FileSystem = PrivateAttr()

    def __init__(
        self,
        id: Optional[str] = None,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content: Optional[Dict[str, str]] = None,
        bucket: Optional[str] = None,
        prefix: str = "",
        fs: Optional[s3fs.S3FileSystem] = None,
    ) -> None:
        super().__init__()
        self.id = id if id else str(uuid.uuid4())
        self.version = version if version else "1.0.0"
        self.metadata = metadata if metadata else {}
        self.content = content if content else {}

        if "program_id" not in self.metadata:
            self.metadata["program_id"] = self.id
        if "program_version" not in self.metadata:
            self.metadata["program_version"] = self.version
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.utcnow().isoformat()

        self.bucket = bucket
        self.prefix = prefix
        self._fs = fs or self._create_memory_fs()

    # ------------------------------------------------------------------
    @staticmethod
    def _create_memory_fs() -> s3fs.S3FileSystem:
        store = fsspec.filesystem("memory")

        class _FS(s3fs.S3FileSystem):
            def __init__(self) -> None:
                super().__init__(anon=True)
                self.store = store

            def open(self, path: str, mode: str = "r", **kwargs):  # type: ignore[override]
                return store.open(path, mode, **kwargs)

            def glob(self, path: str, **kwargs):
                return store.glob(path, **kwargs)

            def isdir(self, path: str):  # type: ignore[override]
                return store.isdir(path)

            def exists(self, path: str):  # type: ignore[override]
                return store.exists(path)

            def makedirs(self, path: str, exist_ok: bool = False):
                store.mkdirs(path, exist_ok=exist_ok)

        return _FS()

    # ------------------------------------------------------------------
    @classmethod
    def from_s3(
        cls,
        bucket: str,
        prefix: str = "",
        fs: Optional[s3fs.S3FileSystem] = None,
    ) -> "MemoryS3FSProgram":
        fs = fs or cls._create_memory_fs()
        root_path = f"{bucket}/{prefix}".rstrip("/")
        content: Dict[str, str] = {}
        for path in fs.glob(f"{root_path}/**"):
            if fs.isdir(path):
                continue
            if path.endswith((".py", ".txt", ".md")):
                with fs.open(path, "r") as fh:
                    rel = path[len(root_path) + 1 :]
                    content[rel] = fh.read()
        return cls(bucket=bucket, prefix=prefix, fs=fs, content=content)

    def save_to_s3(
        self, bucket: Optional[str] = None, prefix: Optional[str] = None
    ) -> None:
        bucket = bucket or self.bucket
        prefix = prefix or self.prefix
        if not bucket:
            raise ValueError("Bucket must be specified")
        root_path = f"{bucket}/{prefix}".rstrip("/")
        for rel, text in self.content.items():
            dest = f"{root_path}/{rel}".rstrip("/")
            folder = dest.rsplit("/", 1)[0]
            if not self._fs.exists(folder):
                self._fs.makedirs(folder, exist_ok=True)
            with self._fs.open(dest, "w") as fh:
                fh.write(text)

