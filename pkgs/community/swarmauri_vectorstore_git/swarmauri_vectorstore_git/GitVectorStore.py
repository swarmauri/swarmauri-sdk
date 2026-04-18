import json
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional, Tuple, Union

from pydantic import Field, PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase
from swarmauri_base.vector_stores.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri_standard.distances.CosineDistance import CosineDistance
from swarmauri_standard.documents.Document import Document
from swarmauri_standard.embeddings.TfidfEmbedding import TfidfEmbedding


ScopeLiteral = Literal["head", "ref", "all_refs"]
KindLiteral = Literal["commit", "log"]


@ComponentBase.register_type(VectorStoreBase, "GitVectorStore")
class GitVectorStore(VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal["GitVectorStore"] = "GitVectorStore"
    repo_path: Optional[str] = None
    scope: ScopeLiteral = "head"
    ref: Optional[str] = None
    document_kinds: Tuple[KindLiteral, ...] = Field(default=("commit", "log"))
    include_diff_stats: bool = True
    max_commits: Optional[int] = None
    auto_index: bool = False

    _distance = PrivateAttr()
    _embedder = PrivateAttr()
    _document_map = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._distance = CosineDistance()
        self._embedder = TfidfEmbedding()
        self._document_map: Dict[str, Document] = {}
        self.documents = []
        if self.auto_index and self.repo_path:
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
        self._embedder = TfidfEmbedding()

    def build_index(self) -> None:
        self._validate_repo()
        documents = []
        for oid in self._iter_commit_oids():
            metadata = self._collect_commit_metadata(oid)
            if "commit" in self.document_kinds:
                documents.append(self._build_commit_document(metadata))
            if "log" in self.document_kinds:
                documents.append(self._build_log_document(metadata))
        self._document_map = {document.id: document for document in documents}
        self.documents = documents
        self._reindex_documents()

    def refresh_index(self) -> None:
        self.build_index()

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        if not self.documents and self.repo_path:
            self.build_index()

        if not self.documents:
            return []

        query_vector = self._embedder.transform([query])[0]
        document_vectors = [document.embedding for document in self.documents]
        distances = self._distance.distances(query_vector, document_vectors)
        top_k_indices = sorted(range(len(distances)), key=lambda index: distances[index])[
            :top_k
        ]
        return [self.documents[index] for index in top_k_indices]

    def query(self, text: str, top_k: int = 5) -> List[Document]:
        return self.retrieve(text, top_k=top_k)

    def save_store(self, directory_path: str) -> None:
        output_dir = Path(directory_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "repo_path": self.repo_path,
            "scope": self.scope,
            "ref": self.ref,
            "document_kinds": list(self.document_kinds),
            "include_diff_stats": self.include_diff_stats,
            "max_commits": self.max_commits,
            "documents": [document.model_dump(mode="json") for document in self.documents],
        }
        (output_dir / "git_vectorstore.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    def load_store(self, directory_path: str) -> None:
        payload = json.loads(
            (Path(directory_path) / "git_vectorstore.json").read_text(encoding="utf-8")
        )
        self.repo_path = payload.get("repo_path")
        self.scope = payload.get("scope", "head")
        self.ref = payload.get("ref")
        self.document_kinds = tuple(payload.get("document_kinds", ["commit", "log"]))
        self.include_diff_stats = payload.get("include_diff_stats", True)
        self.max_commits = payload.get("max_commits")
        self.documents = [Document.model_validate(document) for document in payload["documents"]]
        self._document_map = {document.id: document for document in self.documents}
        self._reindex_documents()

    def _reindex_documents(self) -> None:
        if not self.documents:
            self._embedder = TfidfEmbedding()
            return

        vectors = self._embedder.fit_transform([document.content for document in self.documents])
        for document, vector in zip(self.documents, vectors):
            document.embedding = vector

    def _validate_repo(self) -> None:
        if not self.repo_path:
            raise ValueError("repo_path is required to build the git index")
        repo_path = Path(self.repo_path)
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository path '{self.repo_path}' does not exist")
        self._run_git("rev-parse", "--git-dir")

    def _iter_commit_oids(self) -> Iterable[str]:
        args: List[str] = ["rev-list"]
        if self.scope == "all_refs":
            args.append("--all")
        elif self.scope == "ref":
            if not self.ref:
                raise ValueError("ref is required when scope='ref'")
            args.append(self.ref)
        else:
            args.append("HEAD")

        if self.max_commits:
            args.extend(["--max-count", str(self.max_commits)])

        output = self._run_git(*args)
        return [line.strip() for line in output.splitlines() if line.strip()]

    def _collect_commit_metadata(self, oid: str) -> Dict[str, Union[str, List[str], Dict[str, str], None]]:
        fields = self._run_git(
            "show",
            "--quiet",
            "--format=%H%x00%P%x00%an%x00%ae%x00%aI%x00%cn%x00%ce%x00%cI%x00%s%x00%B",
            oid,
        ).split("\x00", 9)
        if len(fields) != 10:
            raise RuntimeError(f"Unexpected metadata payload for commit '{oid}'")

        changed_paths = self._run_git(
            "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", oid
        )
        stats = ""
        if self.include_diff_stats:
            stats = self._run_git("show", "--stat", "--format=", "--summary", oid)
        log_text = self._run_git(
            "log",
            "-1",
            "--stat",
            "--decorate=short",
            "--date=iso-strict",
            "--format=fuller",
            oid,
        )

        return {
            "oid": fields[0].strip(),
            "parents": [parent for parent in fields[1].split() if parent],
            "author_name": fields[2].strip(),
            "author_email": fields[3].strip(),
            "authored_at": fields[4].strip(),
            "committer_name": fields[5].strip(),
            "committer_email": fields[6].strip(),
            "committed_at": fields[7].strip(),
            "subject": fields[8].strip(),
            "body": fields[9].strip(),
            "changed_paths": [line.strip() for line in changed_paths.splitlines() if line.strip()],
            "stats": stats.strip(),
            "log_text": log_text.strip(),
            "scope": self.scope,
            "ref": self.ref,
        }

    def _build_commit_document(self, metadata: Dict[str, Union[str, List[str], None]]) -> Document:
        changed_paths = metadata["changed_paths"] or []
        stats = metadata["stats"] or ""
        content_lines = [
            f"commit {metadata['oid']}",
            f"scope {metadata['scope']}",
            f"ref {metadata['ref'] or 'HEAD'}",
            f"subject {metadata['subject']}",
            f"author {metadata['author_name']} <{metadata['author_email']}>",
            f"committer {metadata['committer_name']} <{metadata['committer_email']}>",
            f"authored_at {metadata['authored_at']}",
            f"committed_at {metadata['committed_at']}",
            f"parents {' '.join(metadata['parents']) if metadata['parents'] else '(root)'}",
        ]
        if metadata["body"]:
            content_lines.extend(["", "message", str(metadata["body"]).strip()])
        if changed_paths:
            content_lines.extend(["", "changed_paths", *changed_paths])
        if stats:
            content_lines.extend(["", "diff_stats", str(stats)])

        return Document(
            id=f"{metadata['oid']}:commit",
            content="\n".join(content_lines).strip(),
            metadata={
                "oid": metadata["oid"],
                "kind": "commit",
                "scope": metadata["scope"],
                "ref": metadata["ref"],
                "parents": metadata["parents"],
                "changed_paths": changed_paths,
                "subject": metadata["subject"],
                "author": {
                    "name": metadata["author_name"],
                    "email": metadata["author_email"],
                    "time": metadata["authored_at"],
                },
                "committer": {
                    "name": metadata["committer_name"],
                    "email": metadata["committer_email"],
                    "time": metadata["committed_at"],
                },
            },
        )

    def _build_log_document(self, metadata: Dict[str, Union[str, List[str], None]]) -> Document:
        return Document(
            id=f"{metadata['oid']}:log",
            content=str(metadata["log_text"]).strip(),
            metadata={
                "oid": metadata["oid"],
                "kind": "log",
                "scope": metadata["scope"],
                "ref": metadata["ref"],
                "subject": metadata["subject"],
            },
        )

    def _run_git(self, *args: str) -> str:
        if not self.repo_path:
            raise ValueError("repo_path must be configured before running git commands")

        completed = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")
        return completed.stdout
