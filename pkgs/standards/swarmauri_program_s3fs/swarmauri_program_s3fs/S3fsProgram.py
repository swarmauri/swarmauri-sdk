from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

import s3fs
from pydantic import PrivateAttr
from swarmauri_base.programs.ProgramBase import ProgramBase

logger = logging.getLogger(__name__)


class S3fsProgram(ProgramBase):
    """Program backed by S3 using ``s3fs``."""

    _program_type: ClassVar[str] = "s3fs"
    type: str = "S3fsProgram"
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
        self._fs = fs or s3fs.S3FileSystem()

    # ------------------------------------------------------------------
    @classmethod
    def from_s3(
        cls,
        bucket: str,
        prefix: str = "",
        fs: Optional[s3fs.S3FileSystem] = None,
    ) -> "S3fsProgram":
        """Load program files from an S3 location."""
        fs = fs or s3fs.S3FileSystem()
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
        """Save program content to S3."""
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
