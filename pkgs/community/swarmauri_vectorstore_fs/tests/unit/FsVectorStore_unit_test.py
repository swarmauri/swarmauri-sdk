from pathlib import Path

import pytest

from swarmauri_vectorstore_fs import FsVectorStore
from swarmauri_vectorstore_fs.cli import main as cli_main


@pytest.fixture
def sample_tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "src" / "search").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "src" / "search" / "FsVectorStore.py").write_text(
        "\n".join(
            [
                "class FsVectorStore:",
                "    def register_vector_store(self):",
                "        return 'vector store registration'",
                "    def chunk_documents(self):",
                "        return 'chunk identity path aware retrieval'",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "auth_token.md").write_text(
        "authentication token rotation guide\n",
        encoding="utf-8",
    )
    (root / "notes.txt").write_text("plain body search target\n", encoding="utf-8")
    (root / "image.bin").write_bytes(b"\x00\x01binary")
    return root


@pytest.mark.unit
def test_bm25f_field_weighting_favors_filename_match(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "auth_token.md").write_text("plain content\n", encoding="utf-8")
    (root / "notes.md").write_text("auth token reference\n", encoding="utf-8")

    store = FsVectorStore(root_path=root.as_posix(), mode="file")
    store.build_index()
    results = store.retrieve("auth token", top_k=2)

    assert results
    assert results[0].metadata["relative_path"] == "auth_token.md"


@pytest.mark.unit
def test_oov_terms_do_not_crash_and_present_terms_still_rank(sample_tree: Path):
    store = FsVectorStore(root_path=sample_tree.as_posix(), mode="chunk")
    store.build_index()

    results = store.retrieve("notpresentanywhere auth", top_k=3)

    assert results
    assert results[0].metadata["relative_path"] == "docs/auth_token.md"


@pytest.mark.unit
def test_all_zero_query_returns_no_results(sample_tree: Path):
    store = FsVectorStore(root_path=sample_tree.as_posix(), mode="chunk")
    store.build_index()

    assert store.retrieve("zzzzzz_nonexistent_term", top_k=3) == []


@pytest.mark.unit
def test_modes_produce_expected_document_counts(sample_tree: Path):
    chunk_store = FsVectorStore(root_path=sample_tree.as_posix(), mode="chunk", chunk_size=10_000)
    file_store = FsVectorStore(root_path=sample_tree.as_posix(), mode="file", chunk_size=10_000)
    chunk_file_store = FsVectorStore(
        root_path=sample_tree.as_posix(),
        mode="chunk_file",
        chunk_size=10_000,
    )

    chunk_store.build_index()
    file_store.build_index()
    chunk_file_store.build_index()

    assert len(chunk_store.documents) == 3
    assert len(file_store.documents) == 3
    assert len(chunk_file_store.documents) == 6
    assert {doc.metadata["document_kind"] for doc in chunk_file_store.documents} == {
        "chunk",
        "file",
    }
    assert chunk_store.index_metadata["binary"] == 1


@pytest.mark.unit
def test_chunk_identity_fields_are_stable_and_indexed(sample_tree: Path):
    store = FsVectorStore(
        root_path=sample_tree.as_posix(),
        mode="chunk",
        chunk_size=40,
        chunk_overlap=0,
        include=("src/search/FsVectorStore.py",),
    )
    store.build_index()

    assert len(store.documents) > 1
    first = store.documents[0]
    second = store.documents[1]
    assert first.metadata["chunk_global_index"] == 0
    assert second.metadata["chunk_global_index"] == 1
    assert first.metadata["chunk_path_index"] == 0
    assert second.metadata["chunk_path_index"] == 1
    assert first.metadata["chunk_file_index"] == 0
    assert second.metadata["chunk_file_index"] == 1
    assert "chunk_global_1" in second.metadata["bm25_fields"]["chunk_identity"]


@pytest.mark.unit
def test_retrieval_by_body_filename_path_extension_and_chunk_number(sample_tree: Path):
    store = FsVectorStore(
        root_path=sample_tree.as_posix(),
        mode="chunk",
        chunk_size=40,
        chunk_overlap=0,
    )
    store.build_index()

    assert store.retrieve("registration", top_k=1)[0].metadata["relative_path"].endswith(
        "FsVectorStore.py"
    )
    assert store.retrieve("FsVectorStore", top_k=1)[0].metadata["relative_path"].endswith(
        "FsVectorStore.py"
    )
    assert store.retrieve("src search", top_k=1)[0].metadata["relative_path"].endswith(
        "FsVectorStore.py"
    )
    assert store.retrieve("md", top_k=1)[0].metadata["relative_path"] == "docs/auth_token.md"
    assert store.retrieve("chunk_global_1", top_k=1)[0].metadata["chunk_global_index"] == 1


@pytest.mark.unit
def test_save_and_load_preserves_retrieval(sample_tree: Path, tmp_path: Path):
    store = FsVectorStore(root_path=sample_tree.as_posix(), mode="chunk")
    store.build_index()
    output_dir = tmp_path / "store"
    store.save_store(output_dir.as_posix())

    loaded = FsVectorStore()
    loaded.load_store(output_dir.as_posix())

    assert len(loaded.documents) == len(store.documents)
    assert loaded.index_metadata == store.index_metadata
    assert loaded.retrieve("auth token", top_k=1)[0].metadata["relative_path"] == "docs/auth_token.md"


@pytest.mark.unit
def test_cli_query_json_and_show(sample_tree: Path):
    store = FsVectorStore(root_path=sample_tree.as_posix(), mode="chunk")
    store.build_index()
    document_id = store.retrieve("registration", top_k=1)[0].id

    assert cli_main(["--root", sample_tree.as_posix(), "query", "--query", "registration", "--json"]) == 0
    assert cli_main(["--root", sample_tree.as_posix(), "show", "--document-id", document_id]) == 0
