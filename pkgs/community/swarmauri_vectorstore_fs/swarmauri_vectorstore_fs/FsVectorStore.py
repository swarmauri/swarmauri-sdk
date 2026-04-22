import fnmatch
import json
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional, Tuple, Union

from pydantic import Field, PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase
from swarmauri_base.vector_stores.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri_standard.documents.Document import Document

from .BM25FScorer import BM25FScorer


ModeLiteral = Literal["chunk", "file", "chunk_file"]
DEFAULT_EXCLUDE_PATTERNS = (
    ".git/**",
    "**/.git/**",
    "__pycache__/**",
    "**/__pycache__/**",
    ".venv/**",
    "**/.venv/**",
    "node_modules/**",
    "**/node_modules/**",
)


@ComponentBase.register_type(VectorStoreBase, "FsVectorStore")
class FsVectorStore(VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal["FsVectorStore"] = "FsVectorStore"
    root_path: Optional[str] = None
    mode: ModeLiteral = "chunk"
    chunk_size: int = 1200
    chunk_overlap: int = 120
    include: Tuple[str, ...] = Field(default=())
    exclude: Tuple[str, ...] = Field(default=())
    max_file_size: int = 1_000_000
    auto_index: bool = False
    index_metadata: Dict[str, int] = Field(default_factory=dict)

    _scorer = PrivateAttr()
    _document_map = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scorer = BM25FScorer()
        self._document_map: Dict[str, Document] = {}
        self.documents = []
        if self.auto_index and self.root_path:
            self.build_index()

    def add_document(self, document: Document) -> None:
        self._document_map[document.id] = document
        self.documents = list(self._document_map.values())
        self._reindex_documents()

    def add_documents(self, documents: List[Document]) -> None:
        for document in documents:
            self._document_map[document.id] = document
        self.documents = list(self._document_map.values())
        self._reindex_documents()

    def get_document(self, id: str) -> Union[Document, None]:
        return self._document_map.get(id)

    def get_all_documents(self) -> List[Document]:
        return list(self.documents)

    def update_document(self, id: str, updated_document: Document) -> None:
        if id not in self._document_map:
            raise KeyError(f"Document '{id}' not found")
        self._document_map[id] = updated_document
        self.documents = list(self._document_map.values())
        self._reindex_documents()

    def delete_document(self, id: str) -> None:
        self._document_map.pop(id, None)
        self.documents = list(self._document_map.values())
        self._reindex_documents()

    def clear_documents(self) -> None:
        self.documents = []
        self._document_map = {}
        self._scorer = BM25FScorer()

    def build_index(self) -> None:
        root = self._validate_root()
        documents: List[Document] = []
        skip_counts = {
            "binary": 0,
            "oversized": 0,
            "unreadable": 0,
            "excluded": 0,
        }
        global_index = 0

        for file_index, path in enumerate(self._iter_indexable_files(root, skip_counts)):
            relative_path = path.relative_to(root).as_posix()
            text = self._read_text(path, skip_counts)
            if text is None:
                continue

            chunks = self._chunk_text(text)
            if self.mode in {"chunk", "chunk_file"}:
                for chunk_file_index, (chunk, start_line, end_line) in enumerate(chunks):
                    document = self._build_document(
                        relative_path=relative_path,
                        file_index=file_index,
                        chunk_global_index=global_index,
                        chunk_path_index=chunk_file_index,
                        chunk_file_index=chunk_file_index,
                        start_line=start_line,
                        end_line=end_line,
                        document_kind="chunk",
                        content=chunk,
                    )
                    documents.append(document)
                    global_index += 1

            if self.mode in {"file", "chunk_file"}:
                document = self._build_document(
                    relative_path=relative_path,
                    file_index=file_index,
                    chunk_global_index=global_index,
                    chunk_path_index=len(chunks),
                    chunk_file_index=-1,
                    start_line=1,
                    end_line=self._line_count(text),
                    document_kind="file",
                    content=text,
                )
                documents.append(document)
                global_index += 1

        self.index_metadata = {
            **skip_counts,
            "indexed_documents": len(documents),
        }
        self._document_map = {document.id: document for document in documents}
        self.documents = documents
        self._reindex_documents()

    def refresh_index(self) -> None:
        self.build_index()

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        return [document for document, _score in self.search(query, top_k=top_k)]

    def query(self, text: str, top_k: int = 5) -> List[Document]:
        return self.retrieve(text, top_k=top_k)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        if not self.documents and self.root_path:
            self.build_index()
        results = self._scorer.search(query, top_k=top_k)
        return [(self.documents[index], score) for index, score in results]

    def save_store(self, directory_path: str) -> None:
        output_dir = Path(directory_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "root_path": self.root_path,
            "mode": self.mode,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "include": list(self.include),
            "exclude": list(self.exclude),
            "max_file_size": self.max_file_size,
            "index_metadata": self.index_metadata,
            "bm25f": self._scorer.to_dict(),
            "documents": [document.model_dump(mode="json") for document in self.documents],
        }
        (output_dir / "fs_vectorstore.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    def load_store(self, directory_path: str) -> None:
        payload = json.loads(
            (Path(directory_path) / "fs_vectorstore.json").read_text(encoding="utf-8")
        )
        self.root_path = payload.get("root_path")
        self.mode = payload.get("mode", "chunk")
        self.chunk_size = payload.get("chunk_size", 1200)
        self.chunk_overlap = payload.get("chunk_overlap", 120)
        self.include = tuple(payload.get("include", []))
        self.exclude = tuple(payload.get("exclude", []))
        self.max_file_size = payload.get("max_file_size", 1_000_000)
        self.index_metadata = payload.get("index_metadata", {})
        self.documents = [Document.model_validate(document) for document in payload["documents"]]
        self._document_map = {document.id: document for document in self.documents}
        self._scorer = BM25FScorer.from_dict(payload.get("bm25f", {}))
        if not self._scorer.document_fields:
            self._reindex_documents()

    def _reindex_documents(self) -> None:
        self._scorer = BM25FScorer()
        self._scorer.fit([self._fields_for_document(document) for document in self.documents])

    def _validate_root(self) -> Path:
        if not self.root_path:
            raise ValueError("root_path is required to build the filesystem index")
        root = Path(self.root_path)
        if not root.exists():
            raise FileNotFoundError(f"Root path '{self.root_path}' does not exist")
        if not root.is_dir():
            raise NotADirectoryError(f"Root path '{self.root_path}' is not a directory")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap must be zero or greater")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return root

    def _iter_indexable_files(self, root: Path, skip_counts: Dict[str, int]) -> Iterable[Path]:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative_path = path.relative_to(root).as_posix()
            if self.include and not self._matches_any(relative_path, self.include):
                skip_counts["excluded"] += 1
                continue
            if self._matches_any(relative_path, (*DEFAULT_EXCLUDE_PATTERNS, *self.exclude)):
                skip_counts["excluded"] += 1
                continue
            yield path

    def _read_text(self, path: Path, skip_counts: Dict[str, int]) -> Optional[str]:
        try:
            size = path.stat().st_size
            if size > self.max_file_size:
                skip_counts["oversized"] += 1
                return None
            data = path.read_bytes()
        except OSError:
            skip_counts["unreadable"] += 1
            return None

        if b"\x00" in data:
            skip_counts["binary"] += 1
            return None

        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            skip_counts["binary"] += 1
            return None

    def _chunk_text(self, text: str) -> List[Tuple[str, int, int]]:
        if not text:
            return [("", 1, 1)]

        chunks: List[Tuple[str, int, int]] = []
        start = 0
        text_length = len(text)
        while start < text_length:
            end = min(text_length, start + self.chunk_size)
            chunk = text[start:end]
            start_line = text.count("\n", 0, start) + 1
            end_line = text.count("\n", 0, end) + 1
            chunks.append((chunk, start_line, end_line))
            if end == text_length:
                break
            start = max(end - self.chunk_overlap, start + 1)
        return chunks

    def _build_document(
        self,
        *,
        relative_path: str,
        file_index: int,
        chunk_global_index: int,
        chunk_path_index: int,
        chunk_file_index: int,
        start_line: int,
        end_line: int,
        document_kind: Literal["chunk", "file"],
        content: str,
    ) -> Document:
        path = Path(relative_path)
        file_name = path.name
        file_extension = path.suffix
        directory_path = path.parent.as_posix() if path.parent.as_posix() != "." else ""
        bm25_fields = self._build_bm25_fields(
            relative_path=relative_path,
            directory_path=directory_path,
            file_name=file_name,
            file_extension=file_extension,
            file_index=file_index,
            chunk_global_index=chunk_global_index,
            chunk_path_index=chunk_path_index,
            chunk_file_index=chunk_file_index,
            content=content,
        )
        metadata = {
            "relative_path": relative_path,
            "file_index": file_index,
            "file_name": file_name,
            "file_extension": file_extension,
            "chunk_global_index": chunk_global_index,
            "chunk_path_index": chunk_path_index,
            "chunk_file_index": chunk_file_index,
            "start_line": start_line,
            "end_line": end_line,
            "document_kind": document_kind,
            "bm25_fields": bm25_fields,
        }
        return Document(
            id=f"fs:{file_index}:{document_kind}:{chunk_path_index}",
            content=self._composite_content(metadata, content),
            metadata=metadata,
        )

    def _build_bm25_fields(
        self,
        *,
        relative_path: str,
        directory_path: str,
        file_name: str,
        file_extension: str,
        file_index: int,
        chunk_global_index: int,
        chunk_path_index: int,
        chunk_file_index: int,
        content: str,
    ) -> Dict[str, str]:
        chunk_identity = " ".join(
            [
                f"file_index {file_index}",
                f"file_{file_index}",
                f"chunk_global_index {chunk_global_index}",
                f"chunk_global_{chunk_global_index}",
                f"chunk_path_index {chunk_path_index}",
                f"chunk_path_{chunk_path_index}",
                f"chunk_file_index {chunk_file_index}",
                f"chunk_file_{chunk_file_index}",
            ]
        )
        return {
            "file_name": file_name,
            "relative_path": relative_path,
            "directory_path": directory_path,
            "file_extension": file_extension,
            "chunk_identity": chunk_identity,
            "content": content,
        }

    def _fields_for_document(self, document: Document) -> Dict[str, str]:
        fields = document.metadata.get("bm25_fields")
        if isinstance(fields, dict):
            return {field: str(value) for field, value in fields.items()}
        return {
            "file_name": str(document.metadata.get("file_name", "")),
            "relative_path": str(document.metadata.get("relative_path", "")),
            "directory_path": str(Path(str(document.metadata.get("relative_path", ""))).parent),
            "file_extension": str(document.metadata.get("file_extension", "")),
            "chunk_identity": " ".join(
                str(document.metadata.get(key, ""))
                for key in (
                    "file_index",
                    "chunk_global_index",
                    "chunk_path_index",
                    "chunk_file_index",
                )
            ),
            "content": document.content,
        }

    def _composite_content(self, metadata: Dict, content: str) -> str:
        return "\n".join(
            [
                f"file_index: {metadata['file_index']}",
                f"file_path: {metadata['relative_path']}",
                f"file_name: {metadata['file_name']}",
                f"file_extension: {metadata['file_extension']}",
                f"chunk_global_index: {metadata['chunk_global_index']}",
                f"chunk_path_index: {metadata['chunk_path_index']}",
                f"chunk_file_index: {metadata['chunk_file_index']}",
                f"document_kind: {metadata['document_kind']}",
                "content:",
                content,
            ]
        )

    def _matches_any(self, relative_path: str, patterns: Tuple[str, ...]) -> bool:
        path = relative_path.replace("\\", "/")
        name = Path(path).name
        return any(fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(name, pattern) for pattern in patterns)

    def _line_count(self, text: str) -> int:
        if not text:
            return 1
        return text.count("\n") + (0 if text.endswith("\n") else 1)
